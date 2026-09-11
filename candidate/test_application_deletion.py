from django.contrib.auth.models import User
from django.test import TestCase

from recruiter.models import Job
from .models import CandidateProfile, JobApplication


class CandidateApplicationDeletionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="candidate", password="TestPass123!")
        self.profile = CandidateProfile.objects.create(user=self.user)
        self.job = Job.objects.create(
            title="Python Developer",
            company="Test Company",
            location="Hyderabad",
            salary="5 LPA",
            job_type="Full-Time",
            experience="0-2 years",
            skills="Python, Django",
            description="Test job",
        )
        self.application = JobApplication.objects.create(
            candidate=self.profile,
            job=self.job,
            ats_score=50,
            matching_percentage=50,
            matched_skills="Python",
            missing_skills="Django",
        )

    def test_candidate_can_delete_own_application(self):
        self.client.login(username="candidate", password="TestPass123!")
        response = self.client.post(
            f"/candidate/applications/{self.application.id}/delete/"
        )
        self.assertRedirects(response, "/candidate/applications/")
        self.assertFalse(JobApplication.objects.filter(id=self.application.id).exists())

    def test_candidate_cannot_delete_another_candidates_application(self):
        other_user = User.objects.create_user(username="other", password="TestPass123!")
        other_profile = CandidateProfile.objects.create(user=other_user)
        other_application = JobApplication.objects.create(
            candidate=other_profile,
            job=self.job,
        )

        self.client.login(username="candidate", password="TestPass123!")
        response = self.client.post(
            f"/candidate/applications/{other_application.id}/delete/"
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(JobApplication.objects.filter(id=other_application.id).exists())
