from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .models import Job
from candidate.models import JobApplication, Interview, Notification
from .forms import JobForm
from django.db.models import Q


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


def recruiter_logout(request):
    logout(request)
    return redirect("recruiter_login")


# ==========================
# Recruiter Dashboard
# ==========================
@login_required(login_url="/recruiter/login/")
def dashboard(request):
    jobs = Job.objects.all()

    context = {
        "total_jobs": jobs.count(),
        "active_jobs": jobs.count(),
        "closed_jobs": 0,
        "recent_jobs": jobs.order_by("-posted_date")[:5],
    }

    return render(request, "recruiter/dashboard.html", context)


# ==========================
# Post Job
# ==========================
@login_required(login_url="/recruiter/login/")
def post_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Job posted successfully.")
            return redirect("view_jobs")

    else:
        form = JobForm()

    return render(request, "recruiter/post_job.html", {"form": form})


# ==========================
# View Jobs
# ==========================
@login_required(login_url="/recruiter/login/")
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
        {"jobs": jobs}
    )


# ==========================
# Job Details
# ==========================
@login_required(login_url="/recruiter/login/")
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(
        request,
        "recruiter/job_details.html",
        {"job": job}
    )


# ==========================
# Edit Job
# ==========================
@login_required(login_url="/recruiter/login/")
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect("view_jobs")

    else:
        form = JobForm(instance=job)

    return render(
        request,
        "recruiter/post_job.html",
        {"form": form}
    )


# ==========================
# Delete Job
# ==========================
@login_required(login_url="/recruiter/login/")
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect("view_jobs")

    return render(
        request,
        "recruiter/delete_job.html",
        {"job": job}
    )


# ==========================
# Recruiter Profile
# ==========================
@login_required(login_url="/recruiter/login/")
def profile(request):
    return render(request, "recruiter/profile.html")


# ==========================
# Applications
# ==========================
@login_required(login_url="/recruiter/login/")
def applications(request):
    applications = JobApplication.objects.select_related(
        "candidate__user",
        "job"
    ).order_by("-applied_date")

    return render(
        request,
        "recruiter/applications.html",
        {"applications": applications}
    )


# ==========================
# Schedule Interview
# ==========================
@login_required(login_url="/recruiter/login/")
def schedule_interview(request, application_id):

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    if request.method == "POST":

        interview_date = request.POST.get("interview_date")

        hour = request.POST.get("interview_hour")
        minute = request.POST.get("interview_minute")
        period = request.POST.get("interview_period")

        # Convert 12-hour time to 24-hour time
        if period == "PM" and hour != "12":
            hour = str(int(hour) + 12)

        elif period == "AM" and hour == "12":
            hour = "00"

        interview_time = f"{hour}:{minute}"

        mode = request.POST.get("mode")
        meeting_link = request.POST.get("meeting_link")
        remarks = request.POST.get("remarks")

        Interview.objects.create(
            application=application,
            interview_date=interview_date,
            interview_time=interview_time,
            mode=mode,
            meeting_link=meeting_link,
            remarks=remarks
        )

        application.status = "Interview"
        application.save()

        Notification.objects.create(
            candidate=application.candidate,
            title="Interview Scheduled",
            message=(
                f"Your interview for {application.job.title} "
                f"has been scheduled on {interview_date} "
                f"at {interview_time}."
            )
        )

        messages.success(
            request,
            "Interview scheduled successfully."
        )

        return redirect("recruiter_applications")

    return render(
        request,
        "recruiter/schedule_interview.html",
        {"application": application}
    )
# ==========================
# Cancel Interview
# ==========================
@login_required(login_url="/recruiter/login/")
def cancel_interview(request, application_id):

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    interview = Interview.objects.filter(
        application=application
    ).order_by("-interview_date", "-interview_time").first()

    if interview:

        interview.delete()

        application.status = "Shortlisted"
        application.save()

        Notification.objects.create(
            candidate=application.candidate,
            title="Interview Cancelled",
            message=(
                f"Your interview for {application.job.title} "
                f"has been cancelled."
            )
        )

        messages.success(
            request,
            "Interview cancelled successfully."
        )

    else:

        messages.error(
            request,
            "No scheduled interview found."
        )

    return redirect("recruiter_applications")