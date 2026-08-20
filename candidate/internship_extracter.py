import re

INTERN_SECTION = re.compile(r"^\s*(?:internships?|internship experience)\s*(?:[:\-–—])?\s*$", re.I)
STOP_HEADING = re.compile(
    r"^\s*(?:projects?|education|skills|technical skills|certifications?|certificates?|achievements?|hackathons?|languages|references|experience|work experience|professional experience)\s*(?:[:\-–—])?\s*$",
    re.I,
)


def extract_internships(text):
    """Extract an internship section, or internship entries from Experience."""
    if not text:
        return ""

    normalized = str(text).replace("\r", "\n").replace("\t", "\n")
    normalized = re.sub(r"[ ]+", " ", normalized)
    lines = [line.strip(" /|") for line in normalized.splitlines()]

    # First preference: a dedicated INTERNSHIPS section.
    for i, line in enumerate(lines):
        if INTERN_SECTION.match(line):
            collected = []
            for candidate in lines[i + 1:]:
                if STOP_HEADING.match(candidate):
                    break
                if candidate:
                    collected.append(candidate)
            if collected:
                return "\n".join(collected).strip()

    # Otherwise, identify internship entries inside Experience. This keeps the
    # output useful for fresher resumes that put internships under Experience.
    internship_markers = re.compile(r"\b(?:intern|internship|trainee|virtual intern)\b", re.I)
    experience_start = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*(?:experience|work experience|professional experience|employment)\s*(?:[:\-–—])?\s*$", line, re.I):
            experience_start = i + 1
            break
    if experience_start is None:
        return ""

    experience_lines = []
    for line in lines[experience_start:]:
        if STOP_HEADING.match(line):
            break
        if line:
            experience_lines.append(line)

    # For resumes that place internships under Experience, retain the complete
    # experience block when it contains internship markers. This avoids losing
    # later internship entries because their descriptions happen to contain
    # words such as "analyst" or "engineer".
    if any(internship_markers.search(line) for line in experience_lines):
        return "\n".join(experience_lines).strip()
    return ""
