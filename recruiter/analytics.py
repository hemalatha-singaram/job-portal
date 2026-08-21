from datetime import timedelta
import csv

from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from candidate.models import Interview, JobApplication, Offer
from .models import Job
from .views import recruiter_only


@recruiter_only
def analytics_dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    jobs = Job.objects.filter(recruiter=request.user)
    applications = JobApplication.objects.filter(
        job__recruiter=request.user
    ).select_related("job", "candidate", "candidate__user")
    interviews = Interview.objects.filter(application__job__recruiter=request.user)
    offers = Offer.objects.filter(application__job__recruiter=request.user)

    total_jobs = jobs.count()
    jobs_last_7 = jobs.filter(posted_date__gte=week_ago).count()
    jobs_last_30 = jobs.filter(posted_date__gte=month_ago).count()

    total_applications = applications.count()
    applications_last_7 = applications.filter(applied_date__gte=week_ago).count()
    applications_last_30 = applications.filter(applied_date__gte=month_ago).count()

    total_candidates = applications.values("candidate_id").distinct().count()
    candidates_last_7 = applications.filter(applied_date__gte=week_ago).values("candidate_id").distinct().count()
    candidates_last_30 = applications.filter(applied_date__gte=month_ago).values("candidate_id").distinct().count()

    status_counts = {
        status: applications.filter(status=status).count()
        for status, _ in JobApplication.STATUS
    }
    shortlisted = status_counts.get("Shortlisted", 0)
    selected = status_counts.get("Selected", 0)
    interview_status_count = status_counts.get("Interview", 0)
    rejected = status_counts.get("Rejected", 0)

    avg_ats = applications.aggregate(value=Avg("ats_score"))["value"] or 0
    highest_ats = applications.order_by("-ats_score").values_list("ats_score", flat=True).first() or 0
    shortlist_rate = round(shortlisted * 100 / total_applications, 1) if total_applications else 0
    selection_rate = round(selected * 100 / total_applications, 1) if total_applications else 0

    top_candidates = applications.order_by("-ats_score", "-applied_date")[:10]
    top_jobs = jobs.annotate(
        application_count=Count("jobapplication", distinct=True),
        average_ats=Avg("jobapplication__ats_score"),
        shortlisted_count=Count(
            "jobapplication",
            filter=Q(jobapplication__status="Shortlisted"),
            distinct=True,
        ),
        interview_count=Count(
            "jobapplication",
            filter=Q(jobapplication__status="Interview"),
            distinct=True,
        ),
        selected_count=Count(
            "jobapplication",
            filter=Q(jobapplication__status="Selected"),
            distinct=True,
        ),
    ).order_by("-application_count", "-posted_date")[:10]

    chart_rows = [
        {"label": label, "value": status_counts.get(label, 0)}
        for label, _ in JobApplication.STATUS
    ]

    context = {
        "total_jobs": total_jobs,
        "jobs_last_7": jobs_last_7,
        "jobs_last_30": jobs_last_30,
        "total_applications": total_applications,
        "applications_last_7": applications_last_7,
        "applications_last_30": applications_last_30,
        "total_candidates": total_candidates,
        "candidates_last_7": candidates_last_7,
        "candidates_last_30": candidates_last_30,
        "shortlisted": shortlisted,
        "interview_status_count": interview_status_count,
        "selected": selected,
        "rejected": rejected,
        "avg_ats": round(float(avg_ats), 1),
        "highest_ats": round(float(highest_ats), 1),
        "shortlist_rate": shortlist_rate,
        "selection_rate": selection_rate,
        "interview_count": interviews.count(),
        "interviews_last_7": interviews.filter(interview_date__gte=week_ago.date()).count(),
        "interviews_last_30": interviews.filter(interview_date__gte=month_ago.date()).count(),
        "candidates_interviewed": interviews.values("application__candidate_id").distinct().count(),
        "offer_count": offers.count(),
        "accepted_offers": offers.filter(accepted=True).count(),
        "top_candidates": top_candidates,
        "top_jobs": top_jobs,
        "chart_rows": chart_rows,
    }
    return render(request, "recruiter/analytics_dashboard.html", context)


@recruiter_only
def analytics_export(request):
    applications = JobApplication.objects.filter(
        job__recruiter=request.user
    ).select_related("job", "candidate", "candidate__user").order_by("-applied_date")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="recruiter_analytics.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Candidate", "Job", "Company", "Status", "ATS Score",
        "Matched Skills", "Missing Skills", "Applied Date",
    ])
    for application in applications:
        writer.writerow([
            application.candidate.user.username,
            application.job.title,
            application.job.company,
            application.status,
            application.ats_score,
            application.matched_skills,
            application.missing_skills,
            application.applied_date.strftime("%Y-%m-%d %H:%M"),
        ])
    return response
