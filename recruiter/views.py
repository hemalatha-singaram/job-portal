from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render

from candidate.models import JobApplication

from .forms import JobForm
from .matching_engine import analyze_application
from .models import CandidateMatch, Job


LOGIN_REQUIRED = '/recruiter/login/'


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


@login_required(login_url=LOGIN_REQUIRED)
def dashboard(request):
    jobs = Job.objects.all().order_by('-posted_date')
    applications = JobApplication.objects.filter(job__in=jobs)

    context = {
        "total_jobs": jobs.count(),
        "active_jobs": jobs.count(),
        "closed_jobs": 0,
        "total_applications": applications.count(),
        "shortlisted_count": applications.filter(status='Shortlisted').count(),
        "interview_count": applications.filter(status='Interview').count(),
        "pending_count": applications.filter(status='Applied').count(),
        "recent_jobs": jobs[:5],
    }

    return render(request, "recruiter/dashboard.html", context)


@login_required(login_url=LOGIN_REQUIRED)
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


@login_required(login_url=LOGIN_REQUIRED)
def view_jobs(request):
    search = request.GET.get("search", "").strip()
    jobs = Job.objects.all().order_by("-posted_date")

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(location__icontains=search)
        )

    jobs = jobs.annotate(application_count=Count('jobapplication', distinct=True))

    return render(request, "recruiter/view_jobs.html", {"jobs": jobs})


@login_required(login_url=LOGIN_REQUIRED)
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    application_count = JobApplication.objects.filter(job=job).count()

    return render(request, "recruiter/job_details.html", {
        "job": job,
        "application_count": application_count,
    })


@login_required(login_url=LOGIN_REQUIRED)
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

    return render(request, "recruiter/post_job.html", {"form": form})


@login_required(login_url=LOGIN_REQUIRED)
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect("view_jobs")

    return render(request, "recruiter/delete_job.html", {"job": job})


@login_required(login_url=LOGIN_REQUIRED)
def profile(request):
    return render(request, "recruiter/profile.html")


# ==========================
# Recruiter ATS / Applications
# ==========================
@login_required(login_url=LOGIN_REQUIRED)
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = list(
        JobApplication.objects.filter(job=job)
        .select_related('candidate__user', 'job')
        .order_by('-applied_date')
    )

    # Ensure every current application has a recruiter-owned ATS record.
    for application in applications:
        if not CandidateMatch.objects.filter(application_id=application.id).exists():
            analyze_application(application)

    applications = list(JobApplication.objects.filter(job=job).select_related(
        'candidate__user', 'job'
    ).order_by('-applied_date'))
    matches = CandidateMatch.objects.filter(application_id__in=[app.id for app in applications])
    match_map = {match.application_id: match for match in matches}
    for application in applications:
        application.recruiter_match = match_map.get(application.id)

    return render(request, "recruiter/job_applications.html", {
        "job": job,
        "applications": applications,
    })


@login_required(login_url=LOGIN_REQUIRED)
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    if request.method != 'POST':
        return redirect('job_applications', job_id=application.job_id)

    status = request.POST.get('status')
    valid_statuses = {choice[0] for choice in JobApplication.STATUS}
    if status not in valid_statuses:
        messages.error(request, 'Invalid application status.')
        return redirect('job_applications', job_id=application.job_id)

    application.status = status
    application.save(update_fields=['status'])
    messages.success(request, f'Application status updated to {status}.')
    return redirect('job_applications', job_id=application.job_id)


@login_required(login_url=LOGIN_REQUIRED)
def save_application_note(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    if request.method == 'POST':
        match, _ = CandidateMatch.objects.get_or_create(application_id=application.id)
        match.notes = request.POST.get('notes', '').strip()
        match.save(update_fields=['notes', 'analyzed_at'])
        messages.success(request, 'Recruiter note saved.')

    return redirect('job_applications', job_id=application.job_id)


@login_required(login_url=LOGIN_REQUIRED)
def ranked_candidates(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = list(
        JobApplication.objects.filter(job=job)
        .select_related('candidate__user', 'job')
    )

    for application in applications:
        if not CandidateMatch.objects.filter(application_id=application.id).exists():
            analyze_application(application)

    matches = CandidateMatch.objects.filter(application_id__in=[app.id for app in applications])
    match_map = {match.application_id: match for match in matches}
    for application in applications:
        application.recruiter_match = match_map.get(application.id)

    sort_by = request.GET.get('sort', 'score')
    if sort_by == 'applied':
        applications.sort(key=lambda item: item.applied_date, reverse=True)
    elif sort_by == 'skills':
        applications.sort(key=lambda item: item.recruiter_match.skills_score, reverse=True)
    elif sort_by == 'experience':
        applications.sort(key=lambda item: item.recruiter_match.experience_score, reverse=True)
    else:
        applications.sort(key=lambda item: item.recruiter_match.overall_score, reverse=True)

    return render(request, "recruiter/ranked_candidates.html", {
        "job": job,
        "applications": applications,
        "sort_by": sort_by,
    })


@login_required(login_url=LOGIN_REQUIRED)
def analyze_candidate(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    analyze_application(application)
    messages.success(request, 'Candidate ATS analysis updated.')
    return redirect('ranked_candidates', job_id=application.job_id)


@login_required(login_url=LOGIN_REQUIRED)
def analyze_all_candidates(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = JobApplication.objects.filter(job=job)
    for application in applications:
        analyze_application(application)
    messages.success(request, f'{applications.count()} candidate(s) analyzed successfully.')
    return redirect('ranked_candidates', job_id=job.id)


@login_required(login_url=LOGIN_REQUIRED)
def candidate_analysis(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related('candidate__user', 'job'),
        id=application_id,
    )
    match = analyze_application(application)

    return render(request, "recruiter/candidate_analysis.html", {
        "application": application,
        "match": match,
    })
