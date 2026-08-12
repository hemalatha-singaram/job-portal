import re


KNOWN_SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "HTML",
    "CSS",
    "Bootstrap",
    "React",
    "Angular",
    "Django",
    "Flask",
    "Node.js",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "NLP",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "AWS",
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "Linux",
    "VS Code",
    "Computer Networks",
    "Network Security",
    "Cyber Security",
    "Cryptography",
    "Firewall",
    "SDN",
    "REST API",
    "REST",
    "API",
]


def extract_skills(text):
    if not text:
        return []

    found_skills = []

    text_lower = text.lower()

    for skill in KNOWN_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills