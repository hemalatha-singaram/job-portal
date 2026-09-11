from django.contrib.auth.models import User
from django.test import TestCase

from candidate.models import CandidateProfile, JobApplication
from .models import Job


class RecruiterApplicationDeletionTests(TestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user(
            username="recruiter", password="TestPass123!", is_staff=True
        )
        self.other_recruiter = User.objects.create_user(
            username="other-recruiter", password="TestPass123!", is_staff=True
        )
        candidate_user = User.objects.create_user(
            username="candidate", password="TestPass123!"
        )
        candidate_profile = CandidateProfile.objects.create(user=candidate_user)

        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title="Python Developer",
            company="Test Company",
            location="Hyderabad",
            salary="5 LPA",
            job_type="Full-Time",
            experience="0-2 years",
            skills="Python, Django",
            description="Test job",
        )
        self.other_job = Job.objects.create(
            recruiter=self.other_recruiter,
            title="Java Developer",
            company="Other Company",
            location="Bengaluru",
            salary="6 LPA",
            job_type="Full-Time",
            experience="1-2 years",
            skills="Java",
            description="Other test job",
        )
        self.application = JobApplication.objects.create(
            candidate=candidate_profile,
            job=self.job,
        )
        self.other_application = JobApplication.objects.create(
            candidate=candidate_profile,
            job=self.other_job,
        )

    def test_recruiter_can_delete_applicant_from_owned_job(self):
        self.client.login(username="recruiter", password="TestPass123!")
        response = self.client.post(
            f"/recruiter/application/{self.application.id}/delete/"
        )
        self.assertRedirects(response, "/recruiter/ats-dashboard/")
        self.assertFalse(JobApplication.objects.filter(id=self.application.id).exists())

    def test_recruiter_cannot_delete_applicant_from_another_recruiters_job(self):
        self.client.login(username="recruiter", password="TestPass123!")
        response = self.client.post(
            f"/recruiter/application/{self.other_application.id}/delete/"
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            JobApplication.objects.filter(id=self.other_application.id).exists()
        )
