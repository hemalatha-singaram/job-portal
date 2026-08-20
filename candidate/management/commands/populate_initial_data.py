from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from candidate.models import CandidateProfile, JobApplication
from recruiter.models import Job


class Command(BaseCommand):
    help = "Populate CampusHire with demo recruiters, candidates, 10 jobs and 10 ranked applications."

    def handle(self, *args, **options):
        self.stdout.write("Preparing CampusHire demo data...")

        recruiter_group, _ = Group.objects.get_or_create(name="Recruiters")

        # Five demo recruiter accounts. The first one is the recommended account for the presentation.
        recruiter_data = [
            ("john_recruiter", "John", "Smith", "john@techcorp.com"),
            ("sarah_recruiter", "Sarah", "Johnson", "sarah@innovate.com"),
            ("mike_recruiter", "Mike", "Brown", "mike@startup.io"),
            ("emily_recruiter", "Emily", "Davis", "emily@globaljobs.com"),
            ("david_recruiter", "David", "Wilson", "david@recruitment.net"),
        ]
        recruiters = []
        for username, first_name, last_name, email in recruiter_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_staff": False,
                },
            )
            user.set_password("RecruiterPass123!")
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.groups.add(recruiter_group)
            user.save()
            recruiters.append(user)

        # Ten candidates make the recruiter ranking screen useful for a live demo.
        candidate_data = [
            ("alex_candidate", "Alex Kumar", "alex@email.com", "Python, Django, PostgreSQL, AWS, Docker", 4),
            ("priya_candidate", "Priya Sharma", "priya@email.com", "Python, Django, REST API, PostgreSQL, Docker", 3),
            ("sophia_candidate", "Sophia Garcia", "sophia@email.com", "Python, Django, AWS, SQL, Docker", 3),
            ("rahul_candidate", "Rahul Mehta", "rahul@email.com", "Python, Django, PostgreSQL, JavaScript", 3),
            ("ananya_candidate", "Ananya Rao", "ananya@email.com", "Python, Django, SQL, AWS", 2),
            ("james_candidate", "James Wilson", "james@email.com", "Python, SQL, JavaScript, Git", 2),
            ("meera_candidate", "Meera Nair", "meera@email.com", "Java, Spring Boot, SQL, Git", 2),
            ("arjun_candidate", "Arjun Patel", "arjun@email.com", "HTML, CSS, JavaScript", 1),
            ("neha_candidate", "Neha Singh", "neha@email.com", "C++, Java, SQL", 1),
            ("vikram_candidate", "Vikram Das", "vikram@email.com", "HTML, CSS", 0),
        ]

        candidates = []
        for index, (username, full_name, email, skills, experience) in enumerate(candidate_data):
            first_name, last_name = full_name.split(" ", 1)
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                },
            )
            user.set_password("CandidatePass123!")
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            profile, _ = CandidateProfile.objects.get_or_create(user=user)
            profile.phone = f"987650{index:04d}"
            profile.city = "Hyderabad"
            profile.state = "Telangana"
            profile.qualification = "B.Tech Computer Science"
            profile.skills = skills
            profile.experience = experience
            profile.experience_level = "Fresher" if experience == 0 else ("1-2 years" if experience < 2 else "2-3 years")
            profile.projects = "CampusHire Recruitment Platform, Resume Intelligence Dashboard"
            profile.keywords = skills
            profile.tags = ", ".join(skills.split(", ")[:3])
            profile.tenth_percentage = 88
            profile.intermediate_percentage = 86
            profile.graduation_percentage = 82
            profile.graduation_cgpa = 8.2
            profile.save()
            candidates.append(profile)

        # Ten visible jobs. Jobs 1-2 belong to the presentation recruiter; the others
        # belong to other recruiters so recruiter ownership can be demonstrated.
        job_data = [
            ("Python Django Developer", "TechCorp India", "Hyderabad, Telangana", "₹12L - ₹18L", "Full-Time", "2+ years", "Python, Django, PostgreSQL, AWS, Docker", 0),
            ("Backend Engineer", "TechCorp India", "Bangalore, Karnataka", "₹14L - ₹20L", "Full-Time", "2+ years", "Python, Django, REST API, PostgreSQL", 0),
            ("Java Spring Boot Developer", "Innovate Tech", "Hyderabad, Telangana", "₹10L - ₹16L", "Full-Time", "2+ years", "Java, Spring Boot, Microservices, SQL", 1),
            ("Frontend React Developer", "StartupHub", "Remote", "₹9L - ₹14L", "Remote", "1+ years", "React, JavaScript, CSS, HTML", 2),
            ("Data Science Engineer", "DataFlow Analytics", "Pune, Maharashtra", "₹12L - ₹18L", "Full-Time", "2+ years", "Python, Machine Learning, SQL, Analytics", 3),
            ("Cloud Engineer", "GlobalSoft Solutions", "Bangalore, Karnataka", "₹13L - ₹19L", "Full-Time", "2+ years", "AWS, Docker, Kubernetes, Linux", 4),
            ("Full Stack Developer", "NextGen Labs", "Chennai, Tamil Nadu", "₹10L - ₹15L", "Full-Time", "1+ years", "Python, React, JavaScript, SQL", 1),
            ("Software Engineer Intern", "TechStart", "Hyderabad, Telangana", "₹35K - ₹50K/month", "Internship", "Fresher", "Python, Git, SQL, Problem Solving", 2),
            ("QA Automation Engineer", "QualityWorks", "Pune, Maharashtra", "₹8L - ₹13L", "Full-Time", "1+ years", "Python, Selenium, SQL, Git", 3),
            ("DevOps Engineer", "CloudScale", "Remote", "₹13L - ₹20L", "Remote", "2+ years", "AWS, Docker, Kubernetes, CI/CD", 4),
        ]

        jobs = []
        now = timezone.now()
        for index, (title, company, location, salary, job_type, experience, skills, recruiter_index) in enumerate(job_data):
            job, _ = Job.objects.get_or_create(title=title, company=company)
            job.recruiter = recruiters[recruiter_index]
            job.location = location
            job.salary = salary
            job.job_type = job_type
            job.experience = experience
            job.skills = skills
            job.description = (
                f"We are looking for a {title} to join {company}.\n\n"
                f"Responsibilities:\n- Build and maintain reliable software\n"
                f"- Collaborate with engineering and product teams\n- Participate in code reviews\n\n"
                f"Required skills: {skills}\n\n"
                "We offer a collaborative environment, learning opportunities and career growth."
            )
            job.posted_date = now - timedelta(days=10 - index)
            job.save()
            jobs.append(job)

        # Exactly ten demo applications for the first recruiter's main job.
        # Scores deliberately cover high, medium and low ranges for the ranking demo.
        demo_job = jobs[0]
        demo_scores = [96, 91, 87, 84, 81, 76, 68, 57, 39, 18]
        statuses = ["Shortlisted", "Shortlisted", "Shortlisted", "Applied", "Applied", "Applied", "Interview", "Applied", "Rejected", "Applied"]

        for index, candidate in enumerate(candidates):
            score = demo_scores[index]
            matched = [s.strip() for s in candidate.skills.split(",") if s.strip() and s.strip().lower() in demo_job.skills.lower()]
            missing = [s.strip() for s in demo_job.skills.split(",") if s.strip().lower() not in candidate.skills.lower()]
            JobApplication.objects.update_or_create(
                candidate=candidate,
                job=demo_job,
                defaults={
                    "phone": candidate.phone,
                    "qualification": candidate.qualification,
                    "cover_letter": "Demo application for CampusHire presentation.",
                    "ats_score": score,
                    "matching_percentage": score,
                    "matched_skills": ", ".join(matched) or "No direct skill match",
                    "missing_skills": ", ".join(missing) or "None",
                    "status": statuses[index],
                    "applied_date": now - timedelta(days=index + 1),
                },
            )

        self.stdout.write(self.style.SUCCESS("\nCampusHire demo data is ready."))
        self.stdout.write(self.style.SUCCESS("  • 5 recruiter accounts"))
        self.stdout.write(self.style.SUCCESS("  • 10 candidate accounts"))
        self.stdout.write(self.style.SUCCESS("  • 10 jobs visible to candidates"))
        self.stdout.write(self.style.SUCCESS("  • 10 applications on the first recruiter's main job"))
        self.stdout.write(self.style.SUCCESS("  • ATS scores: 96, 91, 87, 84, 81, 76, 68, 57, 39, 18"))
        self.stdout.write(self.style.SUCCESS("  • Presentation recruiter: john_recruiter / RecruiterPass123!"))
