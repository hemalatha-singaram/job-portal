from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CandidateProfile, JobApplication, Interview, Offer, Notification

from .forms import (
    RegisterForm,
    ProfileForm,
    JobApplicationForm
)

from recruiter.models import Job
from .resume_parser import extract_resume_text
from .skill_extracter import extract_skills
from .experience_extracter import extract_experience
from .project_extracter import extract_projects
from .keyword_extracter import extract_keywords, generate_tags
from .skill_matcher import match_skills


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            CandidateProfile.objects.create(
                user=user,
                phone='',
                address='',
                city='',
                state='',
                qualification='',
                skills=''
            )

            messages.success(
                request,
                'Student account created. Please login.'
            )

            return redirect('candidate_login')

    else:
        form = RegisterForm()

    return render(
        request,
        'candidate/register.html',
        {'form': form}
    )


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

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'candidate/login.html'
    )


def candidate_logout(request):
    logout(request)
    return redirect('candidate_login')


@login_required
def dashboard(request):

    profile, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'qualification': '',
            'skills': ''
        }
    )

    apps = JobApplication.objects.filter(
        candidate=profile
    )

    return render(
        request,
        'candidate/dashboard.html',
        {
            'applied_count': apps.count(),

            'shortlisted_count':
                apps.filter(status='Shortlisted').count(),

            'interview_count':
                apps.filter(status='Interview').count(),

            'offer_count':
                apps.filter(status='Selected').count(),

            'jobs':
                Job.objects.order_by('-posted_date')[:5]
        }
    )


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
        qs = qs.filter(
            location__icontains=location
        )

    return render(
        request,
        'candidate/jobs.html',
        {'jobs': qs}
    )



@login_required
def job_detail(request, id):

    job = get_object_or_404(
        Job,
        id=id
    )

    profile, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'qualification': '',
            'skills': ''
        }
    )

    applied = JobApplication.objects.filter(
        candidate=profile,
        job=job
    ).exists()

    # Candidate skills
    candidate_skills = [
        skill.strip()
        for skill in profile.skills.split(',')
        if skill.strip()
    ]

    # Match candidate skills with job required skills
    matched, missing, percentage = match_skills(
        candidate_skills,
        job.skills
    )

    return render(
        request,
        'candidate/job_details.html',
        {
            'job': job,
            'applied': applied,
            'matched_skills': matched,
            'missing_skills': missing,
            'matching_percentage': percentage
        }
    )


@login_required
def apply_job(request, id):

    job = get_object_or_404(Job, id=id)

    profile, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'qualification': '',
            'skills': '',
            'resume': ''
        }
    )

    if request.method == 'POST':

        form = JobApplicationForm(request.POST)

        if form.is_valid():

            # Prevent duplicate application
            if JobApplication.objects.filter(
                candidate=profile,
                job=job
            ).exists():

                messages.info(
                    request,
                    'You already applied for this job.'
                )

                return redirect('applications')

            # Candidate skills
            candidate_skills = [
                skill.strip()
                for skill in profile.skills.split(',')
                if skill.strip()
            ]

            # Job required skills
            job_skills = job.skills

            # Match skills
            matched, missing, percentage = match_skills(
                candidate_skills,
                job_skills
            )

            # Create application
            app = form.save(commit=False)

            app.candidate = profile
            app.job = job

            # ATS information
            app.matched_skills = ", ".join(matched)
            app.missing_skills = ", ".join(missing)
            app.matching_percentage = percentage
            app.ats_score = percentage

            app.save()

            messages.success(
                request,
                f'Application submitted successfully. '
                f'Your job match score is {percentage}%.'
            )

            return redirect('applications')

    else:

        form = JobApplicationForm()

    return render(
        request,
        'candidate/apply_job.html',
        {
            'form': form,
            'job': job
        }
    )

@login_required
def my_applications(request):

    profile = get_object_or_404(
        CandidateProfile,
        user=request.user
    )

    applications = JobApplication.objects.filter(
        candidate=profile
    )

    return render(
        request,
        'candidate/my_applications.html',
        {
            'applications': applications
        }
    )


@login_required
def shortlisted(request):

    return my_applications(request)


@login_required
def interviews(request):

    interviews = Interview.objects.filter(
        application__candidate__user=request.user
    )

    return render(
        request,
        'candidate/interviews.html',
        {
            'interviews': interviews
        }
    )


@login_required
def offers(request):

    offers = Offer.objects.filter(
        application__candidate__user=request.user
    )

    return render(
        request,
        'candidate/offers.html',
        {
            'offers': offers
        }
    )


@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        candidate__user=request.user
    )

    return render(
        request,
        'candidate/notifications.html',
        {
            'notifications': notifications
        }
    )


@login_required
def profile(request):

    p, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'qualification': '',
            'skills': '',
            'resume': ''
        }
    )

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=p
        )

        if form.is_valid():

            profile = form.save()

            # Resume processing
            if profile.resume:

                try:
                    # 1. Extract text from resume
                    resume_text = extract_resume_text(
                        profile.resume.path
                    )

                    # 2. Extract skills from resume text
                    extracted_skills = extract_skills(
                        resume_text
                    )

                    extracted_experience = extract_experience( resume_text)
                    extracted_projects = extract_projects(resume_text)
                    extracted_keywords = extract_keywords(resume_text)
                    extracted_tags = generate_tags( extracted_skills, extracted_keywords)

                    # 3. Save extracted information
                    profile.resume_text = resume_text
                    profile.skills = ", ".join(extracted_skills)
                    profile.experience = extracted_experience
                    profile.projects = extracted_projects
                    profile.keywords = ", ".join(extracted_tags)
                    profile.save()

                    messages.success(
                        request,
                        'Resume uploaded and skills extracted successfully.'
                    )

                except Exception as e:

                    messages.error(
                        request,
                        f'Resume processing failed: {e}'
                    )

            else:

                messages.success(
                    request,
                    'Profile updated successfully.'
                )

            return redirect('candidate_profile')

    else:

        form = ProfileForm(instance=p)

    return render(
        request,
        'candidate/profile.html',
        {
            'form': form,
            'profile': p
        }
    )