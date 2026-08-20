"""Keyword/skill extraction from resume text."""

import re

# Broad, practical vocabulary for CampusHire resumes.  Matching is done with
# non-alphanumeric boundaries so symbols in C++, C#, CI/CD and Node.js work.
KNOWN_SKILLS = [
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
    "HTML", "CSS", "Bootstrap", "React", "Angular", "Django", "Flask",
    "Spring", "Spring Boot", "Node.js", "Express.js", "REST API", "API",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase", "Firestore",
    "JDBC", "Hibernate", "Maven", "Kafka",
    "Machine Learning", "Deep Learning", "Artificial Intelligence",
    "Natural Language Processing", "NLP", "Data Science", "Data Analysis",
    "Data Structures", "Algorithms", "Statistics", "Analytics",
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "FAISS",
    "Sentence Transformers", "Sentence-Transformers", "BART", "KeyBERT", "yfinance",
    "AWS", "Azure", "Docker", "Kubernetes", "Linux", "Jenkins", "CI/CD",
    "Git", "GitHub", "GitLab", "VS Code", "Selenium", "ServiceNow", "Postman", "Jupyter", "Bash", "Shell",
    "Power BI", "Tableau", "Excel", "Matplotlib", "Seaborn", "Streamlit",
    "Gemini API", "Gemini", "Problem Solving", "OOP", "Object Oriented Programming",
    "Computer Networks", "Network Security", "Cyber Security", "Cryptography",
    "Firewall", "SDN", "Microservices", "Full Stack Development",
]


def _contains_skill(text_lower, skill):
    escaped = re.escape(skill.lower())
    # C is special because C++ and C# begin with the same character.
    if skill.lower() == "c":
        return bool(re.search(r"(?<![a-z0-9+#])c(?![a-z0-9+#])", text_lower))
    return bool(re.search(r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])", text_lower))


def extract_skills(text):
    if not text:
        return []

    text_lower = str(text).lower()
    found = []
    for skill in KNOWN_SKILLS:
        if _contains_skill(text_lower, skill):
            found.append(skill)

    # Prefer the longer, more specific phrase when a shorter skill is also
    # present (e.g. "Data Analysis" rather than only "Analysis").
    return found
