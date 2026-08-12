from keyword_extracter import extract_keywords, generate_tags


print("TEST STARTED")


resume_text = """
Python Django Python SQL Machine Learning
Python Django Git GitHub
SDN Firewall DDoS Detection
Resume ATS Analyzer
"""


print("Resume text loaded")


skills = [
    "Python",
    "Django",
    "SQL",
    "Machine Learning",
    "Git",
    "GitHub"
]


keywords = extract_keywords(resume_text)

print("Keywords extracted:")
print(keywords)


tags = generate_tags(skills, keywords)

print("Tags generated:")
print(tags)


print("TEST FINISHED")