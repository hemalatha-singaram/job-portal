import re

LANGUAGES = [
    "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript",
    "SQL", "HTML", "CSS", "Bash", "Shell", "R", "Go", "Kotlin", "PHP",
]

TOOLS = [
    "Git", "GitHub", "GitLab", "VS Code", "Excel", "Power BI", "Tableau",
    "Docker", "Kubernetes", "Jenkins", "Kafka", "Postman", "Selenium",
    "ServiceNow", "Firebase", "Firestore", "yfinance", "Jupyter", "Linux",
    "Figma",
]


def _contains(text, value):
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(value.lower()) + r"(?![a-z0-9])", text.lower()))


def extract_languages(text):
    if not text:
        return []
    # Prefer an explicit Languages/Technical Skills section when present, but
    # fall back to the whole resume because languages can appear in projects.
    return [item for item in LANGUAGES if _contains(str(text), item)]


def extract_tools(text):
    if not text:
        return []
    return [item for item in TOOLS if _contains(str(text), item)]
