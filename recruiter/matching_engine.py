import re

from django.utils import timezone

from .models import CandidateMatch


STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'in', 'is', 'of', 'on', 'or', 'the', 'to', 'with', 'we', 'you',
    'your', 'our', 'this', 'that', 'will', 'work', 'working', 'job',
    'role', 'candidate', 'team', 'years', 'year', 'experience',
}


def _tokens(value):
    if not value:
        return set()
    words = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9+#.-]*", str(value).lower())
    return {word.strip('.-') for word in words if word.strip('.-') and word not in STOP_WORDS}


def _skill_tokens(value):
    """Turn common comma/newline/semicolon separated skill lists into tokens."""
    if not value:
        return set()
    parts = re.split(r'[,;|\n]+', str(value))
    tokens = set()
    for part in parts:
        tokens.update(_tokens(part))
    return tokens


def _required_experience(job_experience):
    text = str(job_experience or '').lower()
    numbers = [int(number) for number in re.findall(r'\d+', text)]
    if not numbers:
        return 0
    # For ranges such as "2-4 years", use the minimum expected experience.
    return min(numbers)


def calculate_match(application):
    """Calculate a transparent ATS-style match score for one application."""
    job = application.job
    candidate = application.candidate

    required_skills = _skill_tokens(job.skills)
    candidate_skills = _skill_tokens(candidate.skills)

    if required_skills:
        skill_score = (len(required_skills & candidate_skills) / len(required_skills)) * 100
    else:
        skill_score = 0

    required_experience = _required_experience(job.experience)
    candidate_experience = int(candidate.experience or 0)
    if required_experience <= 0:
        experience_score = 100 if candidate_experience >= 0 else 0
    else:
        experience_score = min(candidate_experience / required_experience, 1) * 100

    job_keywords = _tokens(f'{job.title} {job.description} {job.skills} {job.experience}')
    candidate_keywords = _tokens(
        f'{candidate.skills} {candidate.qualification} {application.cover_letter}'
    )
    if job_keywords:
        keyword_score = (len(job_keywords & candidate_keywords) / len(job_keywords)) * 100
    else:
        keyword_score = 0

    # Skill fit is the strongest signal, followed by experience and keywords.
    overall_score = (
        skill_score * 0.50 +
        experience_score * 0.25 +
        keyword_score * 0.25
    )

    return {
        'overall_score': round(overall_score, 2),
        'skills_score': round(skill_score, 2),
        'experience_score': round(experience_score, 2),
        'keyword_score': round(keyword_score, 2),
    }


def analyze_application(application):
    scores = calculate_match(application)
    match, _ = CandidateMatch.objects.get_or_create(application_id=application.id)
    for field, value in scores.items():
        setattr(match, field, value)
    match.analyzed_at = timezone.now()
    match.save()
    return match
