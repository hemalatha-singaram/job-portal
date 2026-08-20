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
- Authentication uses normal username/email + password login; no email OTP is required.

### Recruiter
- Navigation uses button-style controls.
- Recruiters see and manage only jobs owned by their account.
- Applicant ranking/filtering is scoped to owned jobs.
- Other recruiters' jobs and applications cannot be viewed, edited, deleted or have their application status changed.

## Important

Run `python manage.py migrate` before the first `runserver` after extracting the project. The candidate and recruiter migrations contain the profile/ATS and recruiter-ownership fields used by the final version.


## Final additions
- **Simple authentication:** candidate and recruiter registrations activate accounts immediately; no email OTP/SMTP setup is required.
- **Candidate Analytics Dashboard:** candidate users can open **Analytics** to see Applied, Shortlisted, Interview, Selected/Offer and Rejected counts, plus average ATS score and a doughnut chart.
- **Power BI-ready export:** the Analytics page includes **Export for Power BI**, which downloads a CSV that can be imported into Power BI Desktop.

### Email setup
No email or SMTP configuration is required for registration, login, resume parsing, ATS scoring or analytics.

## Resume Intelligence

- PDF and DOCX resumes are parsed automatically.
- DOCX parsing reads both normal paragraphs and table/cell content, including two-column resume layouts.
- The parser extracts skills, programming languages, tools, projects, internships, hackathons, certificates, education and keywords.
- ATS scoring compares the extracted resume text and skills against the recruiter's required skills with aliases such as PostgreSQL/Postgres, Node.js/NodeJS and REST/REST API.

