from skill_extracter import extract_skills


resume_text = """
Yamini Devi

B.Tech Computer Science

Technical Skills:
Python, Django, SQL, HTML, CSS, JavaScript

Machine Learning:
Pandas, NumPy, Scikit-learn

Tools:
Git, GitHub, Linux

Projects:
SDN Firewall using Python and Machine Learning.
"""


skills = extract_skills(resume_text)

print("========== EXTRACTED SKILLS ==========")

for skill in skills:
    print(skill)