import re

CERT_HEADING = re.compile(r"^\s*(?:certifications?|certificates?|professional certifications?)\s*(?:[:\-–—])?\s*$", re.I)
STOP_HEADING = re.compile(
    r"^\s*(?:projects?|experience|work experience|education|skills|technical skills|achievements?|internships?|hackathon|languages|references)\s*(?:[:\-–—])?\s*$",
    re.I,
)


def extract_certificates(text):
    """Extract certification entries from a resume."""
    if not text:
        return ""
    normalized = str(text).replace("\r", "\n").replace("\t", "\n")
    normalized = re.sub(r"[ ]+", " ", normalized)
    lines = [line.strip(" /|") for line in normalized.splitlines()]

    start = None
    for i, line in enumerate(lines):
        if CERT_HEADING.match(line):
            start = i + 1
            break
        if re.match(r"^certifications?\s*[/|]+$", line, re.I):
            start = i + 1
            break

    if start is None:
        inline = re.search(r"(?im)(?:^|\n)\s*certifications?\s*[:\-/]\s*(.+)$", normalized)
        return inline.group(1).strip() if inline else ""

    collected = []
    for line in lines[start:]:
        if not line:
            continue
        if STOP_HEADING.match(line):
            break
        collected.append(line)
    return "\n".join(collected).strip()
