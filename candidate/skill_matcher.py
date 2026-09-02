import re


# Common resume/job-description variations.  The matcher keeps the displayed
# job skill unchanged while comparing a normalized form underneath.
ALIASES = {
    "nodejs": {"nodejs", "node.js", "node js"},
    "javascript": {"javascript", "java script"},
    "typescript": {"typescript", "type script"},
    "postgresql": {"postgresql", "postgres"},
    "mongodb": {"mongodb", "mongo db"},
    "mysql": {"mysql", "my sql"},
    "restapi": {"rest api", "restful api", "rest"},
    "rest": {"rest", "rest api", "restful api"},
    "machinelearning": {"machine learning", "ml"},
    "deeplearning": {"deep learning", "dl"},
    "artificialintelligence": {"artificial intelligence", "ai"},
    "c++": {"c++", "cpp"},
    "c#": {"c#", "c sharp"},
    "problem-solving": {"problem solving", "problem-solving", "problem solving skills"},
}


def normalize_skill(skill):
    """Normalize a skill for comparison while retaining #/+ where useful."""
    return re.sub(r"[^a-z0-9+#.]", "", str(skill).lower())


def _plain_normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _compact(value):
    return re.sub(r"[^a-z0-9+#]", "", str(value).lower())


def split_skills(value):
    if not value:
        return []
    return [item.strip() for item in re.split(r"[,;\n|]", str(value)) if item.strip()]


def _candidate_variants(skill):
    """Return normalized variants for a candidate skill or required skill."""
    raw = str(skill).strip().lower()
    compact = normalize_skill(raw)
    variants = {compact, _compact(raw), _plain_normalize(raw)}
    variants.update(_compact(alias) for alias in ALIASES.get(compact, set()))
    variants.update(_compact(alias) for alias in ALIASES.get(_compact(raw), set()))
    return {v for v in variants if v}


def _text_contains_skill(text, required_skill):
    """Check a complete resume text, including multi-word skills and aliases."""
    if not text:
        return False

    text_lower = str(text).lower()
    compact_text = _compact(text_lower)
    plain_text = _plain_normalize(text_lower)

    candidates = {str(required_skill).strip().lower()}
    normalized = normalize_skill(required_skill)
    compact_required = _compact(required_skill)
    candidates.update(ALIASES.get(normalized, set()))
    candidates.update(ALIASES.get(compact_required, set()))

    for candidate in candidates:
        candidate = candidate.strip().lower()
        if not candidate:
            continue
        # Phrase-aware match prevents a skill such as SQL from matching MySQL.
        phrase = _plain_normalize(candidate)
        if phrase and re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", plain_text):
            return True
        # Handles forms such as Node.js / C++ / C#.
        compact = _compact(candidate)
        if compact and compact in compact_text:
            # Avoid the common SQL-in-MySQL false positive.
            if compact == "sql" and "mysql" in compact_text:
                if not re.search(r"(?<![a-z0-9])sql(?![a-z0-9])", plain_text):
                    continue
            return True
    return False


def match_skills(candidate_skills, job_skills, candidate_text=""):
    """Match required job skills against extracted skills *and the raw resume text*.

    The raw-text fallback is important because a resume may contain a skill in a
    Projects, Experience, Certifications, or Technologies section that the
    simple skill extractor did not recognize.
    """
    candidate = set()
    for skill in (candidate_skills or []):
        candidate.update(_candidate_variants(skill))

    required = split_skills(job_skills)
    matched, missing = [], []

    for skill in required:
        required_variants = _candidate_variants(skill)
        if candidate.intersection(required_variants) or _text_contains_skill(candidate_text, skill):
            matched.append(skill)
        else:
            missing.append(skill)

    percentage = round((len(matched) / len(required)) * 100, 2) if required else 0
    return matched, missing, percentage
