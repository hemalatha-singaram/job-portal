from django.shortcuts import render, redirect, get_object_or_404
from .models import Job
from .forms import JobForm
from django.db.models import Q

# ==========================
# Recruiter Dashboard
# ==========================
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
def post_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)

        print(request.POST)  # Debug

        if form.is_valid():
            print("Form is valid")
            form.save()
            return redirect("view_jobs")
        else:
            print(form.errors)  # Show validation errors

    else:
        form = JobForm()

    return render(request, "recruiter/post_job.html", {"form": form})

# ==========================
# View Jobs
# ==========================


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
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(request, "recruiter/job_details.html", {
        "job": job
    })


# ==========================
# Edit Job
# ==========================
def edit_job(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":

        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()
            return redirect("view_jobs")

    else:
        form = JobForm(instance=job)

    return render(request, "recruiter/post_job.html", {
        "form": form
    })


# ==========================
# Delete Job
# ==========================
def delete_job(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        job.delete()
        return redirect("view_jobs")

    return render(request, "recruiter/delete_job.html", {
        "job": job
    })
# ==========================
# Recruiter Profile
# ==========================

def profile(request):
    return render(request, "recruiter/profile.html")