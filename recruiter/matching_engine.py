import re

from .models import CandidateMatch


def normalize_skills(text):
    """
    Converts a skills string into a normalized list.

    Supports formats such as:
    Python, Django, SQL

    Python
    Django
    SQL

    Python | Django | SQL
    """

    if not text:
        return []

    text = text.lower()

    parts = re.split(
        r'[,|\n;/]+',
        text
    )

    skills = []

    for part in parts:
        skill = part.strip()

        if skill:
            skills.append(skill)

    return list(dict.fromkeys(skills))


def calculate_ats_score(
    candidate_skills,
    job_skills,
    candidate_experience=0,
    job_experience=""
):
    """
    Calculates a simple ATS score.

    Score:
    - 70% skill match
    - 30% experience match
    """

    candidate_skill_list = normalize_skills(
        candidate_skills
    )

    job_skill_list = normalize_skills(
        job_skills
    )

    if not job_skill_list:
        skill_score = 100
        matched_skills = []
        missing_skills = []

    else:
        matched_skills = []

        for job_skill in job_skill_list:

            for candidate_skill in candidate_skill_list:

                if (
                    job_skill in candidate_skill
                    or candidate_skill in job_skill
                ):
                    matched_skills.append(
                        job_skill
                    )
                    break

        matched_skills = list(
            dict.fromkeys(matched_skills)
        )

        missing_skills = [
            skill
            for skill in job_skill_list
            if skill not in matched_skills
        ]

        skill_score = (
            len(matched_skills)
            / len(job_skill_list)
        ) * 100

    # -------------------------
    # Experience score
    # -------------------------

    experience_score = 100

    try:
        candidate_experience = float(
            candidate_experience or 0
        )
    except (ValueError, TypeError):
        candidate_experience = 0

    required_experience = 0

    if job_experience:

        match = re.search(
            r'\d+',
            str(job_experience)
        )

        if match:
            required_experience = float(
                match.group()
            )

    if required_experience > 0:

        if candidate_experience >= required_experience:
            experience_score = 100

        elif candidate_experience > 0:
            experience_score = (
                candidate_experience
                / required_experience
            ) * 100

            experience_score = min(
                experience_score,
                100
            )

        else:
            experience_score = 0

    # -------------------------
    # Final ATS score
    # -------------------------

    ats_score = (
        (skill_score * 0.70)
        + (experience_score * 0.30)
    )

    ats_score = round(
        min(max(ats_score, 0), 100),
        2
    )

    return {
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": round(skill_score, 2),
        "experience_score": round(
            experience_score,
            2
        ),
    }


def analyze_application(application):
    """
    Analyze one JobApplication and create/update
    its CandidateMatch record.
    """

    candidate = application.candidate
    job = application.job

    result = calculate_ats_score(
        candidate_skills=candidate.skills,
        job_skills=job.skills,
        candidate_experience=candidate.experience,
        job_experience=job.experience
    )

    matched_skills = ", ".join(
        result["matched_skills"]
    )

    missing_skills = ", ".join(
        result["missing_skills"]
    )

    analysis = (
        f"Skill Match: {result['skill_score']}%. "
        f"Experience Match: "
        f"{result['experience_score']}%. "
        f"Final ATS Score: "
        f"{result['ats_score']}%."
    )

    match, created = CandidateMatch.objects.update_or_create(
        application=application,
        defaults={
            "ats_score": result["ats_score"],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "analysis": analysis,
        }
    )

    return match