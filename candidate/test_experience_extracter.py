from experience_extracter import extract_experience


resume_text = """
Yamini Devi

B.Tech Computer Science

Experience:

Software Developer Intern - 6 months

Python Developer - 50 months

Worked on Django and Machine Learning projects.
"""


experience = extract_experience(resume_text)

print("========== EXTRACTED EXPERIENCE ==========")
print("Experience:", experience, "year(s)")