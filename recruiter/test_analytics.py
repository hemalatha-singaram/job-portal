from datetime import date, time

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from candidate.models import CandidateProfile, Interview, JobApplication, Offer
from .models import Job


class RecruiterAnalyticsTests(TestCase):
    def setUp(self):
        group, _ = Group.objects.get_or_create(name="Recruiters")
        self.recruiter = User.objects.create_user(username="recruiter1", password="password123")
        self.recruiter.groups.add(group)
        self.other_recruiter = User.objects.create_user(username="recruiter2", password="password123")
        self.other_recruiter.groups.add(group)
        self.candidate_user = User.objects.create_user(username="candidate1", password="password123")
        self.candidate = CandidateProfile.objects.create(user=self.candidate_user, skills="Python, SQL")
        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title="Data Analyst",
            company="CampusHire",
            location="Hyderabad",
            salary="5 LPA",
            job_type="Full-Time",
            experience="Fresher",
            skills="Python, SQL",
            description="Analytics role",
        )
        self.other_job = Job.objects.create(
            recruiter=self.other_recruiter,
            title="Other Analyst",
            company="OtherCo",
            location="Remote",
            salary="5 LPA",
            job_type="Remote",
            experience="Fresher",
            skills="SQL",
            description="Other role",
        )
        self.application = JobApplication.objects.create(
            candidate=self.candidate,
            job=self.job,
            ats_score=85,
            matched_skills="Python, SQL",
            missing_skills="Power BI",
            status="Shortlisted",
        )
        JobApplication.objects.create(
            candidate=self.candidate,
            job=self.other_job,
            ats_score=95,
            status="Selected",
        )
        Interview.objects.create(
            application=self.application,
            interview_date=date.today(),
            interview_time=time(10, 0),
            mode="Online",
        )
        Offer.objects.create(
            application=self.application,
            salary=500000,
            joining_date=date.today(),
            accepted=True,
        )

    def test_dashboard_shows_only_recruiter_owned_data(self):
        self.client.force_login(self.recruiter)
        response = self.client.get(reverse("recruiter_analytics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_jobs"], 1)
        self.assertEqual(response.context["total_applications"], 1)
        self.assertEqual(response.context["total_candidates"], 1)
        self.assertEqual(response.context["avg_ats"], 85.0)
        self.assertEqual(response.context["highest_ats"], 85.0)
        self.assertEqual(response.context["shortlisted"], 1)
        self.assertEqual(response.context["offer_count"], 1)
        self.assertEqual(response.context["accepted_offers"], 1)
        self.assertEqual(response.context["candidates_interviewed"], 1)

    def test_dashboard_blocks_non_recruiter(self):
        self.client.force_login(self.candidate_user)
        response = self.client.get(reverse("recruiter_analytics"))
        self.assertEqual(response.status_code, 403)

    def test_csv_export_contains_only_owned_applications(self):
        self.client.force_login(self.recruiter)
        response = self.client.get(reverse("recruiter_analytics_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        body = response.content.decode("utf-8")
        self.assertIn("candidate1", body)
        self.assertIn("Data Analyst", body)
        self.assertNotIn("Other Analyst", body)
