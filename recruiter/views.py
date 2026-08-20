from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, time
from .models import Job, CandidateMatch
from .forms import JobForm
from .matching_engine import analyze_application

from candidate.models import (
    JobApplication,
    Interview,
)


LOGIN_REQUIRED = '/recruiter/login/'


# ==========================
# Recruiter Registration
# ==========================
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            group, _ = Group.objects.get_or_create(name="Recruiters")
            user.groups.add(group)

            messages.success(
                request,
                "Recruiter account created. Please login."
            )

            return redirect("recruiter_login")

    return render(request, "recruiter/register.html")


# ==========================
# Recruiter Login
# ==========================
def recruiter_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "recruiter/login.html")


# ==========================
# Recruiter Logout
# ==========================
def recruiter_logout(request):
    logout(request)
    return redirect("recruiter_login")


# ==========================
# Recruiter Dashboard
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def dashboard(request):
    jobs = Job.objects.all()

    context = {
        "total_jobs": jobs.count(),
        "active_jobs": jobs.count(),
        "closed_jobs": 0,
        "recent_jobs": jobs.order_by("-posted_date")[:5],
    }

    return render(
        request,
        "recruiter/dashboard.html",
        context
    )


# ==========================
# Post Job
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def post_job(request):

    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Job posted successfully."
            )

            return redirect("view_jobs")

    else:
        form = JobForm()

    return render(
        request,
        "recruiter/post_job.html",
        {"form": form}
    )


# ==========================
# View Jobs
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def view_jobs(request):

    search = request.GET.get("search")

    jobs = Job.objects.all().order_by("-posted_date")

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company__icontains=search)
            | Q(location__icontains=search)
        )

    return render(
        request,
        "recruiter/view_jobs.html",
        {
            "jobs": jobs
        }
    )


# ==========================
# Job Details
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def job_details(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    return render(
        request,
        "recruiter/job_details.html",
        {
            "job": job
        }
    )


# ==========================
# Edit Job
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def edit_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    if request.method == "POST":

        form = JobForm(
            request.POST,
            instance=job
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Job updated successfully."
            )

            return redirect("view_jobs")

    else:
        form = JobForm(
            instance=job
        )

    return render(
        request,
        "recruiter/post_job.html",
        {
            "form": form
        }
    )


# ==========================
# Delete Job
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def delete_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    if request.method == "POST":

        job.delete()

        messages.success(
            request,
            "Job deleted successfully."
        )

        return redirect("view_jobs")

    return render(
        request,
        "recruiter/delete_job.html",
        {
            "job": job
        }
    )


# ==========================
# Recruiter Profile
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def profile(request):

    return render(
        request,
        "recruiter/profile.html"
    )

# ==========================
# Priority Ranking Candidates
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def priority_ranking(request):
    """
    ATS Dashboard.

    Candidates are analyzed and ranked using:
    - Skill match
    - Experience match
    - ATS score
    - Application status
    """

    # --------------------------------
    # Analyze applications first
    # --------------------------------

    all_applications = JobApplication.objects.select_related(
        "candidate",
        "candidate__user",
        "job"
    ).all()

    for application in all_applications:

        try:
            analyze_application(application)

        except Exception:
            # Do not allow one bad application
            # to break the entire ATS dashboard.
            continue

    # --------------------------------
    # Get fresh queryset with ATS data
    # --------------------------------

    applications = JobApplication.objects.select_related(
        "candidate",
        "candidate__user",
        "job",
        "candidate_match"
    ).all()

    job_id = request.GET.get("job")
    min_score = request.GET.get("min_score")
    min_experience = request.GET.get("min_experience")
    skill_keyword = request.GET.get("skill")
    status = request.GET.get("status")

    # --------------------------------
    # Filter by job
    # --------------------------------

    if job_id:
        applications = applications.filter(
            job_id=job_id
        )

    # --------------------------------
    # Filter by application status
    # --------------------------------

    if status:
        applications = applications.filter(
            status=status
        )

    # --------------------------------
    # Filter by skill
    # --------------------------------

    if skill_keyword:

        applications = applications.filter(
            Q(candidate__skills__icontains=skill_keyword)
            |
            Q(
                candidate_match__matched_skills__icontains=
                skill_keyword
            )
        )

    # --------------------------------
    # Filter by experience
    # --------------------------------

    if min_experience:

        try:

            applications = applications.filter(
                candidate__experience__gte=int(
                    min_experience
                )
            )

        except ValueError:
            pass

    # --------------------------------
    # Filter by ATS score
    # --------------------------------

    if min_score:

        try:

            applications = applications.filter(
                candidate_match__ats_score__gte=float(
                    min_score
                )
            )

        except ValueError:
            pass

    # --------------------------------
    # Highest ATS score first
    # --------------------------------

    applications = applications.order_by(
        "-candidate_match__ats_score"
    )

    # --------------------------------
    # Pagination
    # --------------------------------

    from django.core.paginator import Paginator

    paginator = Paginator(
        applications,
        15
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    # --------------------------------
    # Attach ATS values to applications
    # --------------------------------

    for application in page_obj:

        match = getattr(
            application,
            "candidate_match",
            None
        )

        if match:

            application.ats_score = (
                match.ats_score
            )

            application.matched_skills = (
                match.matched_skills
            )

            application.missing_skills = (
                match.missing_skills
            )

        else:

            application.ats_score = 0
            application.matched_skills = ""
            application.missing_skills = ""

    return render(
        request,
        "recruiter/priority_ranking.html",
        {
            "applications": page_obj,
            "page_obj": page_obj,
            "jobs": Job.objects.all().order_by(
                "title"
            ),
            "status_choices": JobApplication.STATUS,
            "filters": {
                "job": job_id or "",
                "min_score": min_score or "",
                "min_experience": min_experience or "",
                "skill": skill_keyword or "",
                "status": status or "",
            },
        }
    )

# ==========================
# Update Application Status
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def update_application_status(
    request,
    application_id
):

    from candidate.models import Notification

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        if new_status in dict(
            JobApplication.STATUS
        ):

            application.status = new_status
            application.save()

            # Notify candidate
            Notification.objects.create(
                candidate=application.candidate,
                title=f"Application {new_status}",
                message=(
                    f"Your application for "
                    f"{application.job.title} at "
                    f"{application.job.company} "
                    f"is now marked as {new_status}."
                ),
            )

            messages.success(
                request,
                f"Status updated to {new_status}."
            )

        else:

            messages.error(
                request,
                "Invalid status."
            )

    next_url = request.POST.get(
        "next"
    ) or "priority_ranking"

    if next_url == "priority_ranking":
        return redirect(
            "priority_ranking"
        )

    return redirect(
        next_url
    )


# ==========================
# Schedule Interview
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def schedule_interview(
    request,
    application_id
):

    from candidate.models import Notification

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    if request.method == "POST":

        interview_date = request.POST.get(
            "interview_date"
        )

        interview_time = request.POST.get(
            "interview_time"
        )

        mode = request.POST.get(
            "mode"
        )

        meeting_link = request.POST.get(
            "meeting_link",
            ""
        )

        remarks = request.POST.get(
            "remarks",
            ""
        )

        if (
            interview_date
            and interview_time
            and mode
        ):

            Interview.objects.create(
                application=application,
                interview_date=interview_date,
                interview_time=interview_time,
                mode=mode,
                meeting_link=meeting_link,
                remarks=remarks,
            )

            application.status = "Interview"

            application.save()

            # Notify candidate
            Notification.objects.create(
                candidate=application.candidate,
                title="Interview Scheduled",
                message=(
                    f"An interview has been scheduled "
                    f"for your application to "
                    f"{application.job.title} at "
                    f"{application.job.company}."
                ),
            )

            messages.success(
                request,
                "Interview scheduled and candidate notified."
            )

            return redirect(
                "priority_ranking"
            )

        else:

            messages.error(
                request,
                "Please fill in date, time, and mode."
            )

    return render(
        request,
        "recruiter/schedule_interview.html",
        {
            "application": application
        }
    )


# ==========================
# Create Offer
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def create_offer(
    request,
    application_id
):

    from candidate.models import (
        Offer,
        Notification
    )

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    if request.method == "POST":

        salary = request.POST.get(
            "salary"
        )

        joining_date = request.POST.get(
            "joining_date"
        )

        offer_letter = request.FILES.get(
            "offer_letter"
        )

        if (
            salary
            and joining_date
            and offer_letter
        ):

            Offer.objects.update_or_create(
                application=application,
                defaults={
                    "salary": salary,
                    "joining_date": joining_date,
                    "offer_letter": offer_letter,
                }
            )

            application.status = "Selected"

            application.save()

            # Notify candidate
            Notification.objects.create(
                candidate=application.candidate,
                title="Offer Sent",
                message=(
                    f"You've received an offer for "
                    f"{application.job.title} at "
                    f"{application.job.company}. "
                    f"Check your Offers page."
                ),
            )

            messages.success(
                request,
                "Offer created and candidate notified."
            )

            return redirect(
                "priority_ranking"
            )

        else:

            messages.error(
                request,
                "Please fill in salary, joining date, "
                "and attach an offer letter."
            )

    return render(
        request,
        "recruiter/create_offer.html",
        {
            "application": application
        }
    )
# ==========================
# Recruiter Notifications
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def recruiter_notifications(request):

    notifications_list = []

    # ==========================
    # New Applications
    # ==========================
    applications = JobApplication.objects.select_related(
        "candidate__user",
        "job"
    ).order_by("-applied_date")

    for application in applications:

        notifications_list.append({
            "type": "application",
            "message": (
                f"🔔 {application.candidate.user.username} "
                f"applied for {application.job.title}"
            ),
            "date": application.applied_date,
        })

    # ==========================
    # Interviews
    # ==========================
    interviews = Interview.objects.select_related(
        "application__candidate__user",
        "application__job"
    )

    for interview in interviews:

        notifications_list.append({
            "type": "interview",
            "message": (
                f"📅 Interview scheduled for "
                f"{interview.application.candidate.user.username} "
                f"for {interview.application.job.title}"
            ),
            "date": interview.interview_date,
        })

    # ==========================
    # Sort Notifications
    # ==========================
    notifications_list.sort(
        key=lambda item: str(item["date"]),
        reverse=True
    )

    return render(
        request,
        "recruiter/notifications.html",
        {
            "notifications": notifications_list
        }
    )