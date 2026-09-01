# CampusHire — Job Portal

CampusHire is a full-stack recruitment platform built with Django. It connects candidates and recruiters through separate dashboards, resume intelligence, ATS-based candidate evaluation, job applications, recruitment workflow management, analytics, notifications, and basic request/error protection.

Built as a team project by 5 members.

## Current Project Features

### Candidate Module

- Candidate registration and login
- Login using username or email
- Candidate dashboard with application statistics
- Browse, search, and paginate available jobs
- View job details and apply to jobs
- Upload resumes in **PDF and DOCX** formats
- Resume text extraction and profile synchronization
- Automatic extraction of:
  - Skills
  - Programming languages
  - Tools/technologies
  - Projects
  - Internships
  - Work experience
  - Education
  - Certificates
  - Hackathons
  - Keywords and tags
- ATS-style skill matching against job requirements
- ATS score and matched/missing skills for applications
- Application status tracking:
  - Applied
  - Shortlisted
  - Interview
  - Selected
  - Rejected
- Candidate interview and offer pages
- Candidate notifications
- **Candidate Analytics Dashboard** with:
  - Total applications
  - Application status distribution
  - Average ATS score
  - Interview count
  - Offer count
  - Shortlist rate
  - Selection rate
  - Top applications by ATS score
- Export candidate analytics as CSV

### Recruiter Module

- Separate recruiter registration and login
- Recruiter-only access control
- Recruiter dashboard
- Create/post jobs
- View and search owned jobs
- Edit jobs
- Delete jobs
- View job applicant counts
- Candidate priority/ranking screen
- Filter candidates by:
  - Job
  - ATS score
  - Experience
  - Skills
  - Application status
- Candidates are ordered by ATS score for easier shortlisting
- Update candidate application status
- Schedule interviews
- Create and send offers
- Recruiter recruitment activity/notification dashboard showing:
  - New applications
  - Scheduled interviews
  - Offers

### Resume Intelligence / ATS

The application processes the exact resume uploaded for an application before calculating the ATS result. Resume information is extracted and synchronized with the candidate profile.

The ATS matching logic considers the candidate's extracted skills and resume text against the required skills of the selected job and produces:

- ATS score
- Matching percentage
- Matched skills
- Missing skills

Older application results can also be recalculated from the stored resume when possible.

### Notifications & Email

- Portal notifications for candidate recruitment events
- Recruiter-side recruitment activity notifications
- Interview scheduling notifications
- Offer notifications
- Email notification support through Django SMTP
- Email configuration is read from environment variables rather than being stored in source code
- Local development can fall back to Django's console email backend when SMTP credentials are not configured

### Security / Reliability Milestone

The current milestone adds basic protection for multiple requests and unexpected backend errors.

#### Request Rate Limiting

- Limits each client IP to **10 requests per second**
- Requests above the limit receive HTTP **429 Too Many Requests**
- Provides a `Retry-After` response header
- Static and media resources are excluded from the application rate limiter
- Supports normal browser responses as well as AJAX/JSON responses

#### Frontend Error Handling

Unexpected backend exceptions are converted into user-friendly frontend responses instead of exposing raw Django tracebacks.

- Browser requests receive a friendly error page
- AJAX/JSON requests receive a structured error response
- Rate-limited requests receive a dedicated frontend message/page

> For the current project/demo setup, the rate limiter uses Django's local-memory cache. A shared cache such as Redis is recommended for a multi-worker production deployment.

## Demo Data

The repository includes a management command for preparing presentation/demo data.

Running:

```bash
python manage.py populate_initial_data
```

creates or updates:

- **5 recruiter accounts**
- **10 candidate accounts**
- **10 jobs visible to candidates**
- **10 demo applications** for the presentation recruiter's main job
- ATS scores ranging from **96 to 18** to demonstrate candidate ranking

### Presentation Accounts

**Recruiter**

```text
Username: john_recruiter
Password: RecruiterPass123!
```

**Candidates** use the demo candidate accounts created by the command and the common password:

```text
Password: CandidatePass123!
```

Example candidate usernames include:

```text
alex_candidate
priya_candidate
sophia_candidate
rahul_candidate
ananya_candidate
james_candidate
meera_candidate
arjun_candidate
neha_candidate
vikram_candidate
```

## Tech Stack

- **Backend:** Python, Django
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Resume Processing:** PyMuPDF, python-docx
- **Image/File Support:** Pillow
- **Environment Configuration:** python-dotenv
- **Authentication:** Django built-in authentication with separate candidate/recruiter flows
- **Caching:** Django local-memory cache for the demo rate limiter

## Project Structure

```text
job-portal/
├── accounts/       # Authentication/account-related functionality
├── candidate/      # Candidate models, views, resume intelligence, ATS, analytics
├── recruiter/      # Recruiter models, job management, ranking and recruitment workflow
├── profiles/       # Profile utilities
├── config/         # Django settings, URLs, middleware and project configuration
├── static/         # Shared CSS/static files
├── templates/      # Shared templates and frontend error pages
├── media/          # Uploaded resumes/offer files when running locally
├── manage.py
└── requirements.txt
```

## Important Candidate Files

```text
candidate/
├── resume_parser.py              # PDF/DOCX resume text extraction
├── skill_extracter.py            # Skill extraction
├── language_extracter.py         # Programming languages and tools
├── project_extracter.py          # Project extraction
├── internship_extracter.py      # Internship extraction
├── experience_extracter.py      # Experience extraction
├── education_extracter.py       # Education extraction
├── certificate_extracter.py     # Certificate extraction
├── hackathon_extracter.py       # Hackathon extraction
├── keyword_extracter.py         # Keywords/tags
├── skill_matcher.py              # ATS skill matching/scoring
├── views.py                      # Candidate workflows and analytics logic
└── templates/candidate/
    └── analytics_dashboard.html  # Candidate analytics UI
```

## Important Recruiter Files

```text
recruiter/
├── views.py                      # Recruiter workflows, ranking and notifications
├── models.py                     # Job data model
├── forms.py                      # Recruiter job forms
└── templates/recruiter/          # Recruiter dashboard and workflow pages
```

## Reliability Files

```text
config/
├── middleware.py                 # Rate limiting and frontend exception handling
└── settings.py                   # Middleware/cache/email configuration

templates/errors/
├── 429/rate-limited page         # Friendly rate-limit response
└── 500/server-error page         # Friendly server-error response
```

## Setup & Running Locally

```bash
# Clone the repository
git clone https://github.com/hemalatha-singaram/job-portal.git
cd job-portal

# Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Optional: create demo data for presentation
python manage.py populate_initial_data

# Check the Django project
python manage.py check

# Run tests
python manage.py test

# Start the development server
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Testing

The project contains automated tests covering candidate, recruiter, resume intelligence, ATS/skill extraction, analytics-related functionality, and the request/error-handling milestone.

Before presenting or deploying a change, run:

```bash
python manage.py check
python manage.py test
```

Some local Windows environments may encounter temporary-file permission issues in the PDF/DOCX resume tests. These are environment-specific test-file cleanup/access issues and should be verified separately from the application's normal resume-processing flow.

## Milestone Progress

### Completed

- Candidate module
- Recruiter module
- Job posting and management
- Candidate job applications
- Resume upload and PDF/DOCX parsing
- Resume intelligence extraction
- ATS scoring and skill matching
- Candidate analytics dashboard
- Candidate analytics CSV export
- Recruiter candidate priority/ranking
- Interview scheduling
- Offer workflow
- Candidate notifications
- Recruiter recruitment activity notifications
- SMTP/environment-based email configuration
- Demo data population
- Basic request rate limiting
- Frontend-friendly error handling

### Future / Planned Enhancements

- AI-powered job/candidate recommendations
- Skill-gap analysis and learning-path suggestions
- Stronger production security configuration
- JWT/API authentication if an API architecture is introduced
- Production CORS configuration where required
- Distributed rate limiting with Redis or another shared cache
- Further scalability testing for 1000+ users

## Team

| Name | Contribution |
|---|---|
| Hemalatha Singaram | Authentication system, candidate module logic, resume/ATS integration, candidate analytics, project integration |
| Yamini Paturu | Candidate module — models, forms, templates |
| Yashasvi Nagpure | UI/UX — templates and styling |
| Saishivamani | Recruiter module — job posting and management |
| Team Member 5 | Project collaboration and integration |

## License

This project was built for academic purposes.