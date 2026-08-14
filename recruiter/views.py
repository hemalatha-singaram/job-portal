from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db.models import Q
from .models import Job
from candidate.models import JobApplication
from .forms import JobForm


def _is_recruiter(user):
    return user.is_authenticated and user.groups.filter(name='Recruiters').exists()


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif not username or not password:
            messages.error(request, 'Username and password are required.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            group, _ = Group.objects.get_or_create(name='Recruiters')
            user.groups.add(group)
            messages.success(request, 'Recruiter account created. Please login.')
            return redirect('recruiter_login')
    return render(request, 'recruiter/register.html')


def recruiter_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user and _is_recruiter(user):
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid recruiter credentials.')
    return render(request, 'recruiter/login.html')


def recruiter_logout(request):
    logout(request)
    return redirect('recruiter_login')


@login_required(login_url='/recruiter/login/')
def dashboard(request):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    jobs = Job.objects.filter(owner=request.user)
    applications = JobApplication.objects.filter(job__owner=request.user)
    return render(request, 'recruiter/dashboard.html', {
        'total_jobs': jobs.count(),
        'active_jobs': jobs.count(),
        'closed_jobs': 0,
        'application_count': applications.count(),
        'recent_jobs': jobs.order_by('-posted_date')[:5],
    })


@login_required(login_url='/recruiter/login/')
def post_job(request):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.save()
            messages.success(request, 'Job posted successfully.')
            return redirect('view_jobs')
    else:
        form = JobForm()
    return render(request, 'recruiter/post_job.html', {'form': form})


@login_required(login_url='/recruiter/login/')
def view_jobs(request):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    search = request.GET.get('search', '').strip()
    jobs = Job.objects.filter(owner=request.user).order_by('-posted_date')
    if search:
        jobs = jobs.filter(Q(title__icontains=search) | Q(company__icontains=search) | Q(location__icontains=search))
    return render(request, 'recruiter/view_jobs.html', {'jobs': jobs})


@login_required(login_url='/recruiter/login/')
def job_details(request, job_id):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    job = get_object_or_404(Job, id=job_id, owner=request.user)
    return render(request, 'recruiter/job_details.html', {'job': job})


@login_required(login_url='/recruiter/login/')
def edit_job(request, job_id):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    job = get_object_or_404(Job, id=job_id, owner=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('view_jobs')
    else:
        form = JobForm(instance=job)
    return render(request, 'recruiter/post_job.html', {'form': form, 'editing': True})


@login_required(login_url='/recruiter/login/')
def delete_job(request, job_id):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    job = get_object_or_404(Job, id=job_id, owner=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully.')
        return redirect('view_jobs')
    return render(request, 'recruiter/delete_job.html', {'job': job})


@login_required(login_url='/recruiter/login/')
def profile(request):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    return render(request, 'recruiter/profile.html')


@login_required(login_url='/recruiter/login/')
def applications(request):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    applications = JobApplication.objects.select_related('candidate__user', 'job').filter(job__owner=request.user).order_by('-ats_score', '-applied_date')
    return render(request, 'recruiter/applications.html', {
        'applications': applications,
        'status_choices': JobApplication.STATUS,
    })


@login_required(login_url='/recruiter/login/')
def update_application_status(request, application_id):
    if not _is_recruiter(request.user):
        return redirect('recruiter_login')
    application = get_object_or_404(JobApplication, id=application_id, job__owner=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        valid_statuses = {choice[0] for choice in JobApplication.STATUS}
        if status in valid_statuses:
            application.status = status
            application.save(update_fields=['status'])
            messages.success(request, 'Application status updated.')
    return redirect('recruiter_applications')
