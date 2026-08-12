from resume_parser import extract_resume_text


file_path =  r"C:\Users\p. yamini devi\job-portal\media\resumes\1resume.pdf"

text = extract_resume_text(file_path)

print("========== RESUME TEXT ==========")
print(text)