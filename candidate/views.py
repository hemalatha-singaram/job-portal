from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from recruiter.models import Job
from .education_extracter import extract_education
from .hackathon_extracter import extract_hackathons
from .internship_extracter import extract_internships
from .language_extracter import extract_languages, extract_tools
from .experience_extracter import extract_experience
from .forms import JobApplicationForm, ProfileForm, RegisterForm, ResumeUploadForm
from .keyword_extracter import extract_keywords, generate_tags
from .models import CandidateProfile, Interview, JobApplication, Notification, Offer
from .project_extracter import extract_projects
from .certificate_extracter import extract_certificates
from .resume_parser import extract_resume_text
from .skill_extracter import extract_skills
from .skill_matcher import match_skills
#to test the email notification in terminal
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse


def _get_profile(user):
    return CandidateProfile.objects.get_or_create(
        user=user,
        defaults={"phone": "", "address": "", "city": "", "state": "", "qualification": "", "skills": ""},
    )[0]


def _experience_level(years):
    if years >= 5:
        return "5+ years"
    if years >= 3:
        return "3-5 years"
    if years >= 2:
        return "2-3 years"
    if years >= 1:
        return "1-2 years"
    return "<1 year"


def _sync_profile_from_resume(profile, resume_text):
    """Persist all useful resume-derived fields without erasing manual data."""
    extracted_skills = extract_skills(resume_text)
    extracted_experience = extract_experience(resume_text)
    extracted_projects = extract_projects(resume_text)
    extracted_certificates = extract_certificates(resume_text)
    extracted_internships = extract_internships(resume_text)
    extracted_hackathons = extract_hackathons(resume_text)
    extracted_languages = extract_languages(resume_text)
    extracted_tools = extract_tools(resume_text)
    extracted_keywords = extract_keywords(resume_text)
    extracted_tags = generate_tags(extracted_skills, extracted_keywords)
    education = extract_education(resume_text)

    profile.resume_text = resume_text or ""
    if extracted_skills:
        profile.skills = ", ".join(extracted_skills)
    if extracted_experience:
        profile.experience = extracted_experience
        profile.experience_level = _experience_level(extracted_experience)
    if extracted_projects:
        profile.projects = extracted_projects
    if extracted_certificates:
        profile.certificates = extracted_certificates
    if extracted_internships:
        profile.internships = extracted_internships
    if extracted_hackathons:
        profile.hackathons = extracted_hackathons
    if extracted_languages:
        profile.programming_languages = ", ".join(extracted_languages)
    if extracted_tools:
        profile.tools = ", ".join(extracted_tools)
    if extracted_keywords:
        profile.keywords = ", ".join(extracted_keywords)
    if extracted_tags:
        profile.tags = ", ".join(extracted_tags)
    for field, value in education.items():
        if value is not None and getattr(profile, field, None) in (None, ""):
            setattr(profile, field, value)
    profile.save()
    return extracted_skills, extracted_experience, extracted_projects, extracted_certificates, education


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"].lower()
            user.set_password(form.cleaned_data["password"])
            user.is_active = True
            user.save()
            CandidateProfile.objects.create(user=user)
            messages.success(request, "Student account created successfully. You can log in now.")
            return redirect("candidate_login")
    else:
        form = RegisterForm()
    return render(request, "candidate/register.html", {"form": form})


def candidate_login(request):
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
        if authenticated and CandidateProfile.objects.filter(user=authenticated).exists():
            login(request, authenticated)
            return redirect("candidate_dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "candidate/login.html")


def candidate_logout(request):
    logout(request)
    return redirect("candidate_login")


@login_required
def dashboard(request):
    profile = _get_profile(request.user)
    upload_form = ResumeUploadForm()
    if request.method == "POST":
        upload_form = ResumeUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            uploaded_resume = upload_form.cleaned_data["resume"]
            try:
                resume_text = extract_resume_text_from_upload(uploaded_resume)
                profile.resume.save(uploaded_resume.name, uploaded_resume, save=False)
                _sync_profile_from_resume(profile, resume_text)
                messages.success(request, "Resume uploaded. Skills, projects, experience and education were extracted into your profile.")
                return redirect("candidate_dashboard")
            except Exception as exc:
                messages.error(request, f"We could not process this resume: {exc}")
    apps = JobApplication.objects.filter(candidate=profile)
    return render(request, "candidate/dashboard.html", {
        "profile": profile,
        "upload_form": upload_form,
        "applied_count": apps.count(),
        "shortlisted_count": apps.filter(status="Shortlisted").count(),
        "interview_count": apps.filter(status="Interview").count(),
        "offer_count": apps.filter(status="Selected").count(),
        "applications": apps.select_related("job").order_by("-applied_date")[:5],
        "jobs": Job.objects.order_by("-posted_date")[:10],
    })


@login_required
def jobs(request):
    qs = Job.objects.all().order_by("-posted_date")
    keyword = request.GET.get("keyword")
    location = request.GET.get("location")
    if keyword:
        qs = qs.filter(Q(title__icontains=keyword) | Q(company__icontains=keyword) | Q(skills__icontains=keyword))
    if location:
        qs = qs.filter(location__icontains=location)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "candidate/jobs.html", {"jobs": page_obj, "page_obj": page_obj})


@login_required
def job_detail(request, id):
    job = get_object_or_404(Job, id=id)
    profile = _get_profile(request.user)
    application = JobApplication.objects.filter(candidate=profile, job=job).first()
    return render(request, "candidate/job_details.html", {
        "job": job,
        "application": application,
        "applied": application is not None,
    })


@login_required
def apply_job(request, id):
    job = get_object_or_404(Job, id=id)
    profile = _get_profile(request.user)

    existing = JobApplication.objects.filter(candidate=profile, job=job).first()
    if existing:
        return redirect("ats_result", application_id=existing.id)

    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_resume = form.cleaned_data["resume"]

            try:
                # Parse the exact resume used for this application before saving the application.
                resume_text = extract_resume_text_from_upload(uploaded_resume)
                extracted_skills = extract_skills(resume_text)
                extracted_experience = extract_experience(resume_text)
                extracted_projects = extract_projects(resume_text)
                extracted_internships = extract_internships(resume_text)
                extracted_hackathons = extract_hackathons(resume_text)
                extracted_languages = extract_languages(resume_text)
                extracted_tools = extract_tools(resume_text)
                extracted_keywords = extract_keywords(resume_text)
                extracted_tags = generate_tags(extracted_skills, extracted_keywords)
                education = extract_education(resume_text)
            except Exception as exc:
                messages.error(request, f"We could not process this resume: {exc}")
                return render(request, "candidate/apply_job.html", {"form": form, "job": job})

            # Prefer fresh resume extraction for ATS scoring. Fall back to profile skills if extraction is empty.
            candidate_skills = extracted_skills or [s.strip() for s in profile.skills.split(",") if s.strip()]
            matched, missing, percentage = match_skills(candidate_skills, job.skills, candidate_text=resume_text)

            app = form.save(commit=False)
            app.candidate = profile
            app.job = job
            app.matched_skills = ", ".join(matched)
            app.missing_skills = ", ".join(missing)
            app.matching_percentage = percentage
            app.ats_score = percentage
            app.save()

            # Synchronize the candidate profile with the exact resume used for this application.
            _sync_profile_from_resume(profile, resume_text)
            if not profile.phone and app.phone:
                profile.phone = app.phone
            if not profile.qualification and app.qualification:
                profile.qualification = app.qualification
            profile.save()

            messages.success(request, f"Application submitted. Your ATS score is {percentage}%.")
            return redirect("ats_result", application_id=app.id)
    else:
        form = JobApplicationForm(initial={"phone": profile.phone, "qualification": profile.qualification})

    return render(request, "candidate/apply_job.html", {"form": form, "job": job})


def extract_resume_text_from_upload(uploaded_file):
    """Extract text from an uploaded PDF/DOCX without requiring it to be in Media storage first."""
    from tempfile import NamedTemporaryFile
    suffix = ".pdf" if uploaded_file.name.lower().endswith(".pdf") else ".docx"
    with NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        for chunk in uploaded_file.chunks():
            temp.write(chunk)
        temp_path = temp.name
    try:
        uploaded_file.seek(0)
        return extract_resume_text(temp_path)
    finally:
        import os
        try:
            os.remove(temp_path)
        except OSError:
            pass


@login_required
def ats_result(request, application_id):
    profile = _get_profile(request.user)
    application = get_object_or_404(JobApplication.objects.select_related("job"), id=application_id, candidate=profile)

    # Recalculate older applications that were scored before the improved
    # resume-text matcher was introduced. This also fixes an existing 0% ATS
    # result without forcing the candidate to submit the application again.
    if application.resume and application.resume.name:
        try:
            resume_text = extract_resume_text(application.resume.path)
            extracted_skills = extract_skills(resume_text)
            matched, missing, percentage = match_skills(
                extracted_skills, application.job.skills, candidate_text=resume_text
            )
            application.matched_skills = ", ".join(matched)
            application.missing_skills = ", ".join(missing)
            application.matching_percentage = percentage
            application.ats_score = percentage
            application.save(update_fields=[
                "matched_skills", "missing_skills", "matching_percentage", "ats_score"
            ])
        except Exception:
            # Do not break the ATS page if an old uploaded file is unavailable.
            pass
    elif application.ats_score == 0 and profile.resume_text:
        matched, missing, percentage = match_skills(
            [s.strip() for s in profile.skills.split(",") if s.strip()],
            application.job.skills,
            candidate_text=profile.resume_text,
        )
        application.matched_skills = ", ".join(matched)
        application.missing_skills = ", ".join(missing)
        application.matching_percentage = percentage
        application.ats_score = percentage
        application.save(update_fields=[
            "matched_skills", "missing_skills", "matching_percentage", "ats_score"
        ])

    return render(request, "candidate/ats_result.html", {"application": application})


@login_required
def my_applications(request):
    profile = _get_profile(request.user)
    applications = JobApplication.objects.filter(candidate=profile).select_related("job").order_by("-applied_date")
    return render(request, "candidate/my_applications.html", {"applications": applications})


@login_required
def shortlisted(request):
    profile = _get_profile(request.user)
    applications = JobApplication.objects.filter(candidate=profile, status="Shortlisted").select_related("job")
    return render(request, "candidate/my_applications.html", {"applications": applications, "shortlisted_only": True})

    profile = CandidateProfile.objects.get(user=request.user)

    applications = JobApplication.objects.filter(
        candidate=profile,
        status="Shortlisted"
    ).order_by("-applied_date")


    return render(
        request,
        "candidate/shortlisted.html",
        {
            "applications": applications
        }
    )

@login_required
def interviews(request):

    interviews = Interview.objects.filter(application__candidate__user=request.user).select_related("application", "application__job")
    return render(request, "candidate/interviews.html", {"interviews": interviews})

    profile = CandidateProfile.objects.get(user=request.user)

    interviews = Interview.objects.filter(
        application__candidate=profile).order_by("interview_date", "interview_time")
    

    return render(
        request,
        'candidate/interviews.html',
        {
            'interviews': interviews
        }
    )


@login_required
def offers(request):
    offers = Offer.objects.filter(application__candidate__user=request.user).select_related("application", "application__job")
    return render(request, "candidate/offers.html", {"offers": offers})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(candidate__user=request.user).order_by("-created")
    return render(request, "candidate/notifications.html", {"notifications": notifications})


@login_required
def analytics_dashboard(request):
    profile = _get_profile(request.user)
    applications = JobApplication.objects.filter(candidate=profile).select_related("job")
    status_counts = {status: applications.filter(status=status).count() for status, _ in JobApplication.STATUS}
    total = applications.count()
    average_ats = round(sum(app.ats_score for app in applications) / total, 1) if total else 0
    interview_count = Interview.objects.filter(application__candidate=profile).count()
    offer_count = Offer.objects.filter(application__candidate=profile).count()
    shortlisted = status_counts.get("Shortlisted", 0)
    selected = status_counts.get("Selected", 0)
    shortlist_rate = round(shortlisted / total * 100, 1) if total else 0
    selection_rate = round(selected / total * 100, 1) if total else 0
    top_applications = applications.order_by("-ats_score", "-applied_date")[:5]
    chart_labels = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]
    chart_values = [status_counts.get(label, 0) for label in chart_labels]
    return render(request, "candidate/analytics_dashboard.html", {
        "profile": profile,
        "status_counts": status_counts,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "total": total,
        "average_ats": average_ats,
        "interview_count": interview_count,
        "offer_count": offer_count,
        "shortlist_rate": shortlist_rate,
        "selection_rate": selection_rate,
        "top_applications": top_applications,
    })


@login_required
def analytics_export(request):
    import csv
    profile = _get_profile(request.user)
    applications = JobApplication.objects.filter(candidate=profile).select_related("job").order_by("-applied_date")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="campushire_candidate_analytics.csv"'
    writer = csv.writer(response)
    writer.writerow(["Job", "Company", "Location", "Status", "ATS Score", "Matched Skills", "Missing Skills", "Applied Date"])
    for app in applications:
        writer.writerow([app.job.title, app.job.company, app.job.location, app.status, app.ats_score, app.matched_skills, app.missing_skills, app.applied_date.strftime("%Y-%m-%d %H:%M")])
    return response


@login_required
def profile(request):
    p = _get_profile(request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            profile_obj = form.save()
            if profile_obj.resume:
                try:
                    resume_text = extract_resume_text(profile_obj.resume.path)
                    _sync_profile_from_resume(profile_obj, resume_text)
                    messages.success(request, "Profile saved and resume information extracted successfully.")
                except Exception as exc:
                    messages.warning(request, f"Profile saved, but resume extraction could not complete: {exc}")
            else:
                messages.success(request, "Profile updated successfully.")
            return redirect("candidate_profile")
    else:
        form = ProfileForm(instance=p)

    return render(request, "candidate/profile.html", {"form": form, "profile": p})


    return render(
        request,
        'candidate/profile.html',
        {
            'form': form,
            'profile': p
        }
    )

def test_email(request):
    candidate_email = request.user.email
    send_mail(
        subject='Job Portal Test Notification',
        message='Your email notification system is working successfully.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[candidate_email],
        fail_silently=False,
    )

    return HttpResponse(f"Test email sent successfully to {candidate_email}")

