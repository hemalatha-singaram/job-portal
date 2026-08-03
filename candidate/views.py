from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CandidateProfile, JobApplication, Interview, Offer, Notification
from .forms import RegisterForm, ProfileForm, JobApplicationForm
from recruiter.models import Job

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            CandidateProfile.objects.create(user=user, phone='', address='', city='', state='', qualification='', skills='', resume='')
            messages.success(request, 'Student account created. Please login.')
            return redirect('candidate_login')
    else:
        form = RegisterForm()
    return render(request, 'candidate/register.html', {'form': form})

def candidate_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('candidate_dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'candidate/login.html')

def candidate_logout(request):
    logout(request)
    return redirect('candidate_login')

@login_required
def dashboard(request):
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user, defaults={'phone':'','address':'','city':'','state':'','qualification':'','skills':'','resume':''})
    apps = JobApplication.objects.filter(candidate=profile)
    return render(request, 'candidate/dashboard.html', {'applied_count': apps.count(), 'shortlisted_count': apps.filter(status='Shortlisted').count(), 'interview_count': apps.filter(status='Interview').count(), 'offer_count': apps.filter(status='Selected').count(), 'jobs': Job.objects.order_by('-posted_date')[:5]})

@login_required
def jobs(request):
    qs = Job.objects.all().order_by('-posted_date')
    keyword, location = request.GET.get('keyword'), request.GET.get('location')
    if keyword: qs = qs.filter(Q(title__icontains=keyword)|Q(company__icontains=keyword)|Q(skills__icontains=keyword))
    if location: qs = qs.filter(location__icontains=location)
    return render(request, 'candidate/jobs.html', {'jobs': qs})

@login_required
def job_detail(request, id):
    job = get_object_or_404(Job, id=id)
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user, defaults={'phone':'','address':'','city':'','state':'','qualification':'','skills':'','resume':''})
    applied = JobApplication.objects.filter(candidate=profile, job=job).exists()
    return render(request, 'candidate/job_details.html', {'job': job, 'applied': applied})

@login_required
def apply_job(request, id):
    job = get_object_or_404(Job, id=id)
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user, defaults={'phone':'','address':'','city':'','state':'','qualification':'','skills':'','resume':''})
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            if JobApplication.objects.filter(candidate=profile, job=job).exists():
                messages.info(request, 'You already applied for this job.')
                return redirect('applications')
            app = form.save(commit=False); app.candidate=profile; app.job=job; app.save()
            messages.success(request, 'Application submitted successfully.')
            return redirect('applications')
    else: form = JobApplicationForm()
    return render(request, 'candidate/apply_job.html', {'form':form, 'job':job})

@login_required
def my_applications(request):
    profile = get_object_or_404(CandidateProfile, user=request.user)
    return render(request, 'candidate/my_applications.html', {'applications': JobApplication.objects.filter(candidate=profile)})
@login_required
def shortlisted(request): return my_applications(request)
@login_required
def interviews(request): return render(request, 'candidate/interviews.html', {'interviews': Interview.objects.filter(application__candidate__user=request.user)})
@login_required
def offers(request): return render(request, 'candidate/offers.html', {'offers': Offer.objects.filter(application__candidate__user=request.user)})
@login_required
def notifications(request): return render(request, 'candidate/notifications.html', {'notifications': Notification.objects.filter(candidate__user=request.user)})
@login_required
def profile(request):
    p, _ = CandidateProfile.objects.get_or_create(user=request.user, defaults={'phone':'','address':'','city':'','state':'','qualification':'','skills':'','resume':''})
    if request.method == 'POST':
        form=ProfileForm(request.POST, request.FILES, instance=p)
        if form.is_valid(): form.save(); return redirect('candidate_profile')
    else: form=ProfileForm(instance=p)
    return render(request, 'candidate/profile.html', {'form':form})
