import re


def extract_projects(text):
    """
    Extract project information from resume text.
    """

    if not text:
        return ""

    # Look for common project section headings
    pattern = r'(?is)(?:projects?|academic projects?|personal projects?|project experience)\s*[:\-]?\s*(.*?)(?=\n\s*(?:experience|education|skills|technical skills|certifications|achievements|internship|work experience)\s*[:\-]?\s*$|\Z)'

    match = re.search(pattern, text)

    if not match:
        return ""

    projects_text = match.group(1).strip()

    # Clean excessive blank lines
    projects_text = re.sub(r'\n\s*\n+', '\n', projects_text)

    return projects_text