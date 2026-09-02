"""AI-style job recommendations for candidates.

This module is intentionally self-contained so the existing candidate views,
models, and resume-processing pipeline do not need to be rewritten.
"""
import re
from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from recruiter.models import Job
from .models import CandidateProfile, JobApplication


def _tokens(value):
    return set(re.findall(r"[a-z0-9+#.]+", (value or "").lower()))


def _skill_list(value):
    if not value:
        return []
    return [s.strip().lower() for s in re.split(r"[,;|\n]", str(value)) if s.strip()]


def _normalise_skill(value):
    return re.sub(r"[^a-z0-9+#]", "", str(value).lower())


def _skill_match(candidate_skills, job_skills, resume_text=""):
    candidate_values = []
    for skill in candidate_skills:
        candidate_values.extend([_normalise_skill(skill), skill.lower()])

    resume_tokens = _tokens(resume_text)
    matched = []
    missing = []
    for required in _skill_list(job_skills):
        req_norm = _normalise_skill(required)
        req_words = _tokens(required)
        found = req_norm in candidate_values or required in candidate_values
        if not found and req_words:
            found = req_words.issubset(resume_tokens)
        if found:
            matched.append(required)
        else:
            missing.append(required)

    percentage = (len(matched) / len(matched + missing) * 100) if matched or missing else 0
    return matched, missing, round(percentage, 1)


def _text_similarity(left, right):
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    left_counts = Counter(re.findall(r"[a-z0-9+#.]+", (left or "").lower()))
    right_counts = Counter(re.findall(r"[a-z0-9+#.]+", (right or "").lower()))
    common = set(left_counts) & set(right_counts)
    numerator = sum(left_counts[t] * right_counts[t] for t in common)
    left_norm = sum(v * v for v in left_counts.values()) ** 0.5
    right_norm = sum(v * v for v in right_counts.values()) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return round((numerator / (left_norm * right_norm)) * 100, 1)


def _required_years(value):
    text = str(value or "").lower()
    numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text)]
    return min(numbers) if numbers else 0.0


def _experience_score(candidate_years, required_years):
    candidate_years = float(candidate_years or 0)
    required_years = float(required_years or 0)
    if required_years <= 0:
        return 100.0
    if candidate_years >= required_years:
        return 100.0
    return round(max(0.0, candidate_years / required_years * 100), 1)


def _recommendation(candidate, job):
    profile_skills = _skill_list(candidate.skills)
    resume_text = candidate.resume_text or ""
    combined_candidate_text = " ".join([
        candidate.skills or "",
        candidate.projects or "",
        candidate.internships or "",
        candidate.programming_languages or "",
        candidate.tools or "",
        candidate.keywords or "",
        resume_text,
    ])
    matched, missing, skill_score = _skill_match(profile_skills, job.skills, resume_text)
    text_score = _text_similarity(combined_candidate_text, f"{job.title} {job.skills} {job.description}")
    experience_score = _experience_score(candidate.experience, _required_years(job.experience))

    final_score = round(skill_score * 0.65 + text_score * 0.20 + experience_score * 0.15, 1)
    return {
        "job": job,
        "score": final_score,
        "skill_score": skill_score,
        "text_score": text_score,
        "experience_score": experience_score,
        "matched_skills": matched,
        "missing_skills": missing,
    }


@login_required
def recommendations(request):
    """Show jobs ranked for the currently logged-in candidate."""
    try:
        candidate = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        candidate = CandidateProfile.objects.create(user=request.user)

    applied_job_ids = JobApplication.objects.filter(candidate=candidate).values_list("job_id", flat=True)
    jobs = Job.objects.exclude(id__in=applied_job_ids).order_by("-posted_date")
    ranked = [_recommendation(candidate, job) for job in jobs]
    ranked.sort(key=lambda item: (-item["score"], -item["skill_score"], -item["job"].posted_date.timestamp()))

    return render(request, "candidate/ai_recommendations.html", {
        "recommendations": ranked[:20],
        "candidate": candidate,
    })
