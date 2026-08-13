import re


def normalize_skill(skill):
    return re.sub(r'[^a-z0-9+#.]', '', skill.lower())


def match_skills(candidate_skills, job_skills):
    """
    Compare candidate skills with job-required skills.

    Returns:
        matched_skills
        missing_skills
        matching_percentage
    """

    if not job_skills:
        return [], [], 0

    if not candidate_skills:
        missing = [
            skill.strip()
            for skill in job_skills.split(',')
            if skill.strip()
        ]
        return [], missing, 0

    candidate = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    required = [
        skill.strip()
        for skill in job_skills.split(',')
        if skill.strip()
    ]

    matched = []
    missing = []

    for skill in required:
        normalized = normalize_skill(skill)

        if normalized in candidate:
            matched.append(skill)
        else:
            missing.append(skill)

    if required:
        percentage = (len(matched) / len(required)) * 100
    else:
        percentage = 0

    return matched, missing, round(percentage, 2)