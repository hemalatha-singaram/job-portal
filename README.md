# CampusHire — Job Portal

A full-stack job portal built with Django where students create profiles and apply
to job openings, while recruiters post and manage listings from their own dashboard.

Built as a team project by 5 members.

## Features

**Student Panel**
- Register and log in
- Browse and search available jobs
- Apply to jobs with a cover letter
- Track application status (Applied, Shortlisted, Interview, Selected)
- View a personal dashboard with application stats

**Recruiter Panel**
- Register and log in
- Post new job openings
- View, edit, and delete posted jobs
- Manage listings from a dashboard

## Tech Stack

- **Backend:** Python, Django
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap 5
- **Auth:** Django's built-in authentication (separate login flows for students and recruiters)

## Project Structure

```
job-portal/
├── accounts/       # Home page
├── candidate/      # Student-side models, views, templates
├── recruiter/      # Recruiter-side models, views, templates
├── profiles/       # Shared profile utilities
├── config/         # Project settings and root URL configuration
├── static/         # Shared CSS
├── templates/      # Shared base template and home page
└── manage.py
```

## Setup & Running Locally

```bash
# Clone the repo
git clone https://github.com/hemalatha-singaram/job-portal.git
cd job-portal

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up the database
python manage.py migrate

# (Optional) create an admin login
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

## Team

| Name  | Contribution |
|---|---|
| Hemalatha Singaram | Authentication system, candidate module logic, project integration, home page |
| Yamini Paturu      | Candidate module — models, forms, templates |
| Yashasvi Nagpure   | UI/UX — templates and styling |
| Saishivamani       | Recruiter module — job posting and management |

## License

This project was built for academic purposes.