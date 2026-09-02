# CampusHire — Final Clean Version

## Run locally

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Final workflow

### Student
- Professional landing page with separate Student and Recruiter login/sign-up actions.
- Student dashboard includes direct resume upload.
- PDF/DOCX resume parsing automatically updates skills, projects, experience, keywords and education fields when those sections are detected.
- Profile page keeps extracted information visible and editable.
- Job details do not reveal missing skills or a fit score before application.
- Applying requires a resume upload and redirects directly to the job-specific ATS result.
- ATS result shows score, matched skills and missing skills for the submitted resume.
- Forgot password supports email and student phone verification-code flows.

### Recruiter
- Navigation uses button-style controls.
- Recruiters see and manage only jobs owned by their account.
- Applicant ranking/filtering is scoped to owned jobs.
- Other recruiters' jobs and applications cannot be viewed, edited, deleted or have their application status changed.

## Important

Run `python manage.py migrate` before the first `runserver` after extracting the project. The candidate and recruiter migrations contain the profile/ATS and recruiter-ownership fields used by the final version.
