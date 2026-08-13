from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .models import Job
from candidate.models import JobApplication
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
            messages.success(request, "Recruiter account created. Please login.")
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
        "active_jobs": jobs.count(),   # Placeholder
        "closed_jobs": 0,              # Placeholder
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
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(location__icontains=search)
        )

    return render(request, "recruiter/view_jobs.html", {
        "jobs": jobs
    })


# ==========================
# Job Details
# ==========================
@login_required(login_url="/recruiter/login/")
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(request, "recruiter/job_details.html", {
        "job": job
    })


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

    return render(request, "recruiter/post_job.html", {
        "form": form
    })


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

    return render(request, "recruiter/delete_job.html", {
        "job": job
    })
# ==========================
# Recruiter Profile
# ==========================

@login_required(login_url="/recruiter/login/")
def profile(request):
    return render(request, "recruiter/profile.html")


@login_required(login_url="/recruiter/login/")
def applications(request):
    applications = JobApplication.objects.select_related(
        "candidate__user",
        "job"
    ).order_by("-applied_date")

    return render(request, "recruiter/applications.html", {
        "applications": applications
    })
