import re


SECTION_HEADINGS = (
    "experience", "work experience", "professional experience", "employment",
    "education", "academic background", "skills", "technical skills",
    "certifications", "achievements", "internship", "internships",
    "work history", "publications", "references", "languages",
)


def extract_projects(text):
    """Extract the Projects section from a PDF/DOCX resume."""
    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)

    project_heading = re.compile(
        r"^\s*(?:projects?|academic projects?|personal projects?|project experience)\s*(?:[:\-–—])?\s*$",
        re.I,
    )
    stop_heading = re.compile(
        r"^\s*(?:" + "|".join(re.escape(h) for h in SECTION_HEADINGS) + r")\s*(?:[:\-–—])?\s*$",
        re.I,
    )

    lines = normalized.splitlines()
    start = None
    for index, line in enumerate(lines):
        if project_heading.match(line):
            start = index + 1
            break

    if start is None:
        # Also support "Projects: Project A ..." when the heading and first
        # project are on the same line.
        inline = re.search(r"(?im)^\s*(?:projects?|academic projects?|personal projects?|project experience)\s*[:\-–—]\s*(.+)$", normalized)
        if inline:
            tail = inline.group(1).strip()
            return tail
        return ""

    collected = []
    for line in lines[start:]:
        if stop_heading.match(line):
            break
        if line.strip():
            collected.append(line.strip())

    # Keep project bullets/entries readable while avoiding excessive whitespace.
    result = "\n".join(collected)
    result = re.sub(r"\n{2,}", "\n", result).strip()
    return result
