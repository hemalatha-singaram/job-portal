import re


# Common resume/job-description variations. The matcher keeps the displayed
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


def extract_technical_skills(resume_text):
    """Extract only the skills explicitly listed under the Technical Skills section.

    ATS matching intentionally does not infer a skill from projects, experience,
    certifications, summaries, or other resume sections. This keeps the match
    explainable: a skill is matched only when the candidate explicitly lists it
    as a technical skill.
    """
    if not resume_text:
        return []

    lines = [line.strip() for line in str(resume_text).replace("\r", "").split("\n")]
    start = None
    for index, line in enumerate(lines):
        normalized = re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()
        if normalized in {"technical skills", "technical skill", "technical skillset"}:
            start = index + 1
            break

    if start is None:
        return []

    section_headings = {
        "profile summary", "summary", "experience", "work experience",
        "projects", "education", "certifications", "certification",
        "hackathon", "hackathons", "achievements", "awards", "interests",
    }
    section_lines = []
    for line in lines[start:]:
        normalized = re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()
        if normalized in section_headings:
            break
        if line:
            section_lines.append(line)

    skills = []
    for line in section_lines:
        # Remove category labels such as Languages:, Web:, Tools:, etc.
        if ":" in line:
            line = line.split(":", 1)[1]
        # A slash surrounded by whitespace is commonly used as a separator
        # (e.g. Firebase / Firestore), while C/C++ remains untouched.
        parts = re.split(r"[,;|]|\s+/\s+", line)
        for part in parts:
            part = re.sub(r"^[\-•*]+\s*", "", part).strip()
            if part:
                skills.append(part)
    return skills


def match_skills(candidate_skills, job_skills, candidate_text=""):
    """Match required job skills using only the resume's Technical Skills section.

    ``candidate_text`` is retained for backwards compatibility with existing
    callers, but when resume text is supplied it is used only to extract the
    explicit Technical Skills section. No other resume section can create a
    matched skill.
    """
    if candidate_text:
        candidate_skills = extract_technical_skills(candidate_text)

    candidate = set()
    for skill in (candidate_skills or []):
        candidate.update(_candidate_variants(skill))

    required = split_skills(job_skills)
    matched, missing = [], []

    for skill in required:
        required_variants = _candidate_variants(skill)
        if candidate.intersection(required_variants):
            matched.append(skill)
        else:
            missing.append(skill)

    percentage = round((len(matched) / len(required)) * 100, 2) if required else 0
    return matched, missing, percentage
