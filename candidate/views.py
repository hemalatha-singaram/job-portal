from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import CandidateProfile, JobApplication, Interview, Offer, Notification
from .forms import RegisterForm, ProfileForm, JobApplicationForm
from recruiter.models import Job
from .resume_parser import extract_resume_text
from .skill_extracter import extract_skills
from .experience_extracter import extract_experience
from .project_extracter import extract_projects
from .keyword_extracter import extract_keywords, generate_tags
from .skill_matcher import match_skills
from .education_extracter import extract_education


def _profile_for(user):
    profile, _ = CandidateProfile.objects.get_or_create(
        user=user,
        defaults={'skills': ''}
    )
    return profile


def _experience_level(years):
    try:
        years = int(years or 0)
    except (TypeError, ValueError):
        years = 0
    if years <= 0:
        return 'Fresher'
    if years < 1:
        return '<1 year'
    if years <= 2:
        return '1–2 years'
    if years <= 3:
        return '2–3 years'
    if years <= 5:
        return '3–5 years'
    return '5+ years'


def _process_resume(profile):
    """Parse the candidate resume without erasing manually entered values."""
    if not profile.resume:
        return

    resume_text = extract_resume_text(profile.resume.path)
    extracted_skills = extract_skills(resume_text)
    extracted_experience = extract_experience(resume_text)
    extracted_projects = extract_projects(resume_text)
    extracted_keywords = extract_keywords(resume_text)
    extracted_tags = generate_tags(extracted_skills, extracted_keywords)
    education = extract_education(resume_text)

    profile.resume_text = resume_text
    if extracted_skills:
        profile.skills = ', '.join(extracted_skills)
    if extracted_experience is not None and extracted_experience > 0:
        profile.experience = extracted_experience
        profile.experience_level = _experience_level(extracted_experience)
    if extracted_projects:
        profile.projects = extracted_projects
    if extracted_keywords:
        profile.keywords = ', '.join(extracted_keywords)
    if extracted_tags:
        profile.tags = ', '.join(extracted_tags)

    for field, value in education.items():
        if value is not None:
            setattr(profile, field, value)

    profile.save()


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            CandidateProfile.objects.create(user=user, skills='')
            messages.success(request, 'Student account created. Please login.')
            return redirect('candidate_login')
    else:
        form = RegisterForm()
    return render(request, 'candidate/register.html', {'form': form})


def candidate_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
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
    profile = _profile_for(request.user)
    apps = JobApplication.objects.filter(candidate=profile)
    return render(request, 'candidate/dashboard.html', {
        'applied_count': apps.count(),
        'shortlisted_count': apps.filter(status='Shortlisted').count(),
        'interview_count': apps.filter(status='Interview').count(),
        'offer_count': apps.filter(status='Selected').count(),
        'jobs': Job.objects.order_by('-posted_date')[:5],
    })


@login_required
def jobs(request):
    qs = Job.objects.all().order_by('-posted_date')
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    if keyword:
        qs = qs.filter(
            Q(title__icontains=keyword) |
            Q(company__icontains=keyword) |
            Q(skills__icontains=keyword)
        )
    if location:
        qs = qs.filter(location__icontains=location)
    return render(request, 'candidate/jobs.html', {'jobs': qs})


@login_required
def job_detail(request, id):
    job = get_object_or_404(Job, id=id)
    profile = _profile_for(request.user)
    application = JobApplication.objects.filter(candidate=profile, job=job).first()

    context = {
        'job': job,
        'applied': application is not None,
        'application': application,
    }
    if application:
        context.update({
            'matched_skills': [x.strip() for x in application.matched_skills.split(',') if x.strip()],
            'missing_skills': [x.strip() for x in application.missing_skills.split(',') if x.strip()],
            'matching_percentage': application.matching_percentage,
        })
    return render(request, 'candidate/job_details.html', context)


@login_required
def apply_job(request, id):
    job = get_object_or_404(Job, id=id)
    profile = _profile_for(request.user)

    if JobApplication.objects.filter(candidate=profile, job=job).exists():
        messages.info(request, 'You already applied for this job.')
        return redirect('candidate_job_detail', id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the resume to the candidate profile first so the same
            # parsed profile powers future applications and the candidate view.
            profile.resume = form.cleaned_data['resume']
            phone = form.cleaned_data.get('phone', '').strip()
            qualification = form.cleaned_data.get('qualification', '').strip()
            if phone:
                profile.phone = phone
            if qualification:
                profile.qualification = qualification
            profile.save()

            try:
                _process_resume(profile)
            except Exception as exc:
                messages.error(request, f'Resume processing failed: {exc}')
                return render(request, 'candidate/apply_job.html', {'form': form, 'job': job})

            candidate_skills = [s.strip() for s in profile.skills.split(',') if s.strip()]
            matched, missing, percentage = match_skills(candidate_skills, job.skills)

            application = JobApplication.objects.create(
                candidate=profile,
                job=job,
                cover_letter='',
                matched_skills=', '.join(matched),
                missing_skills=', '.join(missing),
                matching_percentage=percentage,
                ats_score=percentage,
            )

            messages.success(request, f'Application submitted. Your ATS fit score is {percentage}%.')
            return redirect('application_result', application_id=application.id)
    else:
        form = JobApplicationForm(initial={
            'phone': profile.phone,
            'qualification': profile.qualification,
        })

    return render(request, 'candidate/apply_job.html', {'form': form, 'job': job})


@login_required
def application_result(request, application_id):
    profile = _profile_for(request.user)
    application = get_object_or_404(JobApplication, id=application_id, candidate=profile)
    return render(request, 'candidate/application_result.html', {
        'application': application,
        'matched_skills': [x.strip() for x in application.matched_skills.split(',') if x.strip()],
        'missing_skills': [x.strip() for x in application.missing_skills.split(',') if x.strip()],
    })


@login_required
def my_applications(request):
    profile = _profile_for(request.user)
    applications = JobApplication.objects.filter(candidate=profile).select_related('job').order_by('-applied_date')
    return render(request, 'candidate/my_applications.html', {'applications': applications})


@login_required
def shortlisted(request):
    return my_applications(request)


@login_required
def interviews(request):
    interviews = Interview.objects.filter(application__candidate__user=request.user)
    return render(request, 'candidate/interviews.html', {'interviews': interviews})


@login_required
def offers(request):
    offers = Offer.objects.filter(application__candidate__user=request.user)
    return render(request, 'candidate/offers.html', {'offers': offers})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(candidate__user=request.user)
    return render(request, 'candidate/notifications.html', {'notifications': notifications})


@login_required
def profile(request):
    p = _profile_for(request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            profile_obj = form.save()
            if profile_obj.resume:
                try:
                    _process_resume(profile_obj)
                    messages.success(request, 'Profile and resume updated successfully.')
                except Exception as exc:
                    messages.error(request, f'Resume processing failed: {exc}')
            else:
                messages.success(request, 'Profile updated successfully.')
            return redirect('candidate_profile')
    else:
        form = ProfileForm(instance=p)

    return render(request, 'candidate/profile.html', {'form': form, 'profile': p})
