from project_extracter import extract_projects


resume_text = """
YAMINI DEVI

B.Tech Computer Science

TECHNICAL SKILLS

Python, Django, SQL, HTML, CSS

PROJECTS

SDN Firewall with DDoS Detection
Developed a firewall using Ryu, Mininet and Python.
Implemented DDoS detection using machine learning.

Resume ATS Analyzer
Developed a Django-based web application for resume analysis
and candidate scoring.

EDUCATION

B.Tech Computer Science
"""


projects = extract_projects(resume_text)

print("========== EXTRACTED PROJECTS ==========")
print(projects)