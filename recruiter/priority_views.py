from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from candidate.models import JobApplication
from .models import Job
from .views import recruiter_only


@recruiter_only
def priority_ranking(request):
    """Recruiter-owned ATS ranking with reliable query-string filters."""
    applications = (
        JobApplication.objects
        .select_related("candidate__user", "job")
        .filter(job__recruiter=request.user)
    )
    owned_jobs = Job.objects.filter(recruiter=request.user).order_by("title")

    job_id = request.GET.get("job", "").strip()
    status = request.GET.get("status", "").strip()
    skill_keyword = request.GET.get("skill", "").strip()
    min_score = request.GET.get("min_score", request.GET.get("ats_min", "")).strip()
    min_experience = request.GET.get("min_experience", "").strip()

    if job_id.isdigit():
        applications = applications.filter(job_id=int(job_id))

    valid_statuses = {value for value, _ in JobApplication.STATUS}
    if status in valid_statuses:
        applications = applications.filter(status=status)

    if skill_keyword:
        applications = applications.filter(
            Q(candidate__skills__icontains=skill_keyword)
            | Q(matched_skills__icontains=skill_keyword)
        )

    # Accept both "70" and UI-style values such as "70+".
    score_text = min_score.rstrip("+").strip()
    if score_text:
        try:
            score = float(score_text)
            score = max(0.0, min(score, 100.0))
            applications = applications.filter(ats_score__gte=score)
        except ValueError:
            min_score = ""

    if min_experience:
        try:
            experience = max(0, int(min_experience))
            applications = applications.filter(candidate__experience__gte=experience)
        except ValueError:
            min_experience = ""

    applications = applications.order_by("-ats_score", "-applied_date")
    paginator = Paginator(applications, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "recruiter/priority_ranking.html", {
        "applications": page_obj,
        "page_obj": page_obj,
        "jobs": owned_jobs,
        "status_choices": JobApplication.STATUS,
        "filters": {
            "job": job_id,
            "status": status,
            "min_score": min_score,
            "min_experience": min_experience,
            "skill": skill_keyword,
        },
    })
