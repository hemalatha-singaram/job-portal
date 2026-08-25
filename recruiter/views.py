from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from candidate.email_utils import send_candidate_notification

from candidate.models import Interview, JobApplication, Notification, Offer
from .forms import JobForm
from .models import Job


def recruiter_only(view_func):
    @wraps(view_func)
    @login_required(login_url="/recruiter/login/")
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.groups.filter(name="Recruiters").exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Recruiter access required.")
    return wrapper


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        try:
            validate_email(email)
            email_error = False
        except ValidationError:
            email_error = True
        if email_error:
            messages.error(request, "Please enter a valid email address.")
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name, is_active=True,
            )
            group, _ = Group.objects.get_or_create(name="Recruiters")
            user.groups.add(group)
            messages.success(request, "Recruiter account created successfully. You can log in now.")
            return redirect("recruiter_login")
    return render(request, "recruiter/register.html")


def recruiter_login(request):
    if request.method == "POST":
        login_value = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = User.objects.filter(username__iexact=login_value).first()
        if not user and "@" in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
        authenticated = authenticate(
            request,
            username=user.username if user else login_value,
            password=password,
        )
        if authenticated and (
            authenticated.is_staff or authenticated.groups.filter(name="Recruiters").exists()
        ):
            login(request, authenticated)
            return redirect("recruiter_dashboard")
        messages.error(request, "Invalid recruiter credentials.")
    return render(request, "recruiter/login.html")


def recruiter_logout(request):
    logout(request)
    return redirect("recruiter_login")


@recruiter_only
def dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user)
    applications = JobApplication.objects.filter(job__recruiter=request.user)
    return render(request, "recruiter/dashboard.html", {
        "total_jobs": jobs.count(),
        "active_jobs": jobs.count(),
        "closed_jobs": 0,
        "total_applications": applications.count(),
        "recent_jobs": jobs.order_by("-posted_date")[:5],
    })


@recruiter_only
def post_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect("view_jobs")
    else:
        form = JobForm()
    return render(request, "recruiter/post_job.html", {"form": form, "is_edit": False})


@recruiter_only
def view_jobs(request):
    search = request.GET.get("search", "").strip()
    jobs = Job.objects.filter(recruiter=request.user).order_by("-posted_date")
    if search:
        jobs = jobs.filter(Q(title__icontains=search) | Q(company__icontains=search) | Q(location__icontains=search))
    return render(request, "recruiter/view_jobs.html", {"jobs": jobs, "search": search})


@recruiter_only
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applicant_count = JobApplication.objects.filter(job=job).count()
    return render(request, "recruiter/job_details.html", {"job": job, "applicant_count": applicant_count})


@recruiter_only
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect("view_jobs")
    else:
        form = JobForm(instance=job)
    return render(request, "recruiter/post_job.html", {"form": form, "is_edit": True, "job": job})


@recruiter_only
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect("view_jobs")
    return render(request, "recruiter/delete_job.html", {"job": job})


@recruiter_only
def profile(request):
    total_jobs = Job.objects.filter(recruiter=request.user).count()
    return render(request, "recruiter/profile.html", {"total_jobs": total_jobs})


@recruiter_only
def priority_ranking(request):
    applications = JobApplication.objects.select_related("candidate", "candidate__user", "job").filter(job__recruiter=request.user)
    owned_jobs = Job.objects.filter(recruiter=request.user).order_by("title")

    job_id = request.GET.get("job", "")
    min_score = request.GET.get("min_score", "")
    min_experience = request.GET.get("min_experience", "")
    skill_keyword = request.GET.get("skill", "").strip()
    status = request.GET.get("status", "")

    if job_id:
        applications = applications.filter(job_id=job_id, job__recruiter=request.user)
    if status:
        applications = applications.filter(status=status)
    if skill_keyword:
        applications = applications.filter(Q(candidate__skills__icontains=skill_keyword) | Q(matched_skills__icontains=skill_keyword))
    if min_experience:
        try:
            applications = applications.filter(candidate__experience__gte=int(min_experience))
        except ValueError:
            pass
    if min_score:
        try:
            applications = applications.filter(ats_score__gte=float(min_score))
        except ValueError:
            pass

    applications = applications.order_by("-ats_score", "-applied_date")
    paginator = Paginator(applications, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "recruiter/priority_ranking.html", {
        "applications": page_obj,
        "page_obj": page_obj,
        "jobs": owned_jobs,
        "status_choices": JobApplication.STATUS,
        "filters": {"job": job_id, "status": status, "min_score": min_score, "min_experience": min_experience, "skill": skill_keyword},
    })


@recruiter_only
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, job__recruiter=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(JobApplication.STATUS):
            application.status = new_status
            application.save(update_fields=["status"])
            Notification.objects.create(
                candidate=application.candidate,
                title=f"Application {new_status}",
                message=f"Your application for {application.job.title} at {application.job.company} is now {new_status}.",
            )
            messages.success(request, f"Application marked as {new_status}.")
        else:
            messages.error(request, "Invalid application status.")
    return redirect("priority_ranking")


@recruiter_only
def schedule_interview(request, application_id):
    application = get_object_or_404(
        JobApplication,
        id=application_id,
        job__recruiter=request.user
    )

    if request.method == "POST":
        date = request.POST.get("interview_date")
        time = request.POST.get("interview_time")
        mode = request.POST.get("mode")
        link = request.POST.get("meeting_link", "")
        remarks = request.POST.get("remarks", "")

        if date and time and mode:

            # Create interview
            Interview.objects.create(
                application=application,
                interview_date=date,
                interview_time=time,
                mode=mode,
                meeting_link=link,
                remarks=remarks
            )

            # Update application status
            application.status = "Interview"
            application.save(update_fields=["status"])

            # Create portal notification
            Notification.objects.create(
                candidate=application.candidate,
                title="Interview Scheduled",
                message=f"An interview has been scheduled for {application.job.title}."
            )

            # Send email notification
            send_candidate_notification(
                application.candidate.user.email,
                "Interview Scheduled - CampusHire",
                f"""
Hello {application.candidate.user.first_name or application.candidate.user.username},

Your interview has been scheduled.

Job: {application.job.title}
Company: {application.job.company}

Date: {date}
Time: {time}
Mode: {mode}
Meeting Link: {link or "Will be provided later"}

Remarks:
{remarks or "No additional remarks."}

Please log in to CampusHire for more details.

Regards,
CampusHire Team
"""
            )

            messages.success(
                request,
                "Interview scheduled successfully and email notification sent."
            )

            return redirect("priority_ranking")

        messages.error(
            request,
            "Please fill in the interview date, time and mode."
        )

    return render(
        request,
        "recruiter/schedule_interview.html",
        {"application": application}
    )

@recruiter_only
def create_offer(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, job__recruiter=request.user)
    if request.method == "POST":
        salary = request.POST.get("salary")
        joining_date = request.POST.get("joining_date")
        offer_letter = request.FILES.get("offer_letter")
        if salary and joining_date and offer_letter:
            Offer.objects.update_or_create(application=application, defaults={"salary": salary, "joining_date": joining_date, "offer_letter": offer_letter})
            application.status = "Selected"
            application.save(update_fields=["status"])
            Notification.objects.create(candidate=application.candidate, title="Offer Sent", message=f"You've received an offer for {application.job.title} at {application.job.company}.")
            messages.success(request, "Offer sent successfully.")
            return redirect("priority_ranking")
        messages.error(request, "Please provide salary, joining date and offer letter.")
    return render(request, "recruiter/create_offer.html", {"application": application})
