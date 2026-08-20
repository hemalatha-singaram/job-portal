import re

SECTION_HEADINGS = (
    "experience", "work experience", "professional experience", "employment",
    "education", "academic background", "skills", "technical skills",
    "certifications", "certification", "achievements", "achievement",
    "internship", "internships", "work history", "publications", "references",
    "languages", "hackathon", "hobbies", "interests",
)

PROJECT_HEADING = re.compile(
    r"^\s*(?:projects?|academic projects?|personal projects?|project experience)"
    r"\s*(?:[:\-–—])?\s*$",
    re.I,
)
STOP_HEADING = re.compile(
    r"^\s*(?:" + "|".join(re.escape(h) for h in SECTION_HEADINGS) + r")"
    r"\s*(?:[:\-–—])?\s*$",
    re.I,
)


def extract_projects(text):
    """Extract the Projects section from PDF/DOCX resume text.

    Handles headings embedded in table cells and common variants such as
    "PROJECTS", "ACADEMIC PROJECTS" and "PROJECT EXPERIENCE".
    """
    if not text:
        return ""

    normalized = str(text).replace("\r", "\n").replace("\t", "\n")
    normalized = re.sub(r"[ ]+", " ", normalized)
    lines = [line.strip(" /|") for line in normalized.splitlines()]

    start = None
    for i, line in enumerate(lines):
        if PROJECT_HEADING.match(line):
            start = i + 1
            break
        # Support headings with a trailing separator such as "PROJECTS /".
        if re.match(r"^(?:projects?|academic projects?|personal projects?|project experience)\s*[/|]+$", line, re.I):
            start = i + 1
            break

    if start is None:
        # If heading and first project share a line, capture the remainder.
        inline = re.search(
            r"(?im)(?:^|\n)\s*(?:projects?|academic projects?|personal projects?|project experience)"
            r"\s*[:\-–—/]\s*(.+)$",
            normalized,
        )
        return inline.group(1).strip() if inline else ""

    collected = []
    for line in lines[start:]:
        if not line:
            continue
        if STOP_HEADING.match(line):
            break
        if re.match(r"^(?:experience|education|technical skills|skills|certifications?|achievements?)\s*[/|:]", line, re.I):
            break
        collected.append(line)

    return "\n".join(collected).strip()
