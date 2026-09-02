from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from candidate.models import CandidateProfile, JobApplication
from recruiter.models import Job


class RecruiterSecurityAndWorkflowTests(TestCase):
    def setUp(self):
        group, _ = Group.objects.get_or_create(name="Recruiters")
        self.r1 = User.objects.create_user(username="r1", password="pass12345"); self.r1.groups.add(group)
        self.r2 = User.objects.create_user(username="r2", password="pass12345"); self.r2.groups.add(group)
        self.profile = CandidateProfile.objects.create(user=User.objects.create_user(username="cand", password="pass12345"), skills="Python")
        self.job1 = Job.objects.create(recruiter=self.r1, title="R1 Python", company="R1Co", location="Hyd", salary="8L", job_type="Full-Time", experience="1", skills="Python", description="x")
        self.job2 = Job.objects.create(recruiter=self.r2, title="R2 Django", company="R2Co", location="Hyd", salary="8L", job_type="Full-Time", experience="1", skills="Django", description="x")
        self.app1 = JobApplication.objects.create(candidate=self.profile, job=self.job1)
        self.app2 = JobApplication.objects.create(candidate=self.profile, job=self.job2)

    def login(self, user):
        self.client.force_login(user)

    def test_recruiter_dashboard_loads_for_recruiter(self):
        self.login(self.r1); self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)

    def test_recruiter_dashboard_excludes_other_jobs(self):
        self.login(self.r1); response = self.client.get(reverse("view_jobs")); self.assertContains(response, "R1 Python"); self.assertNotContains(response, "R2 Django")

    def test_recruiter_job_details_are_owner_scoped(self):
        self.login(self.r1); self.assertEqual(self.client.get(reverse("job_details", args=[self.job2.id])).status_code, 404)

    def test_recruiter_cannot_edit_other_job(self):
        self.login(self.r1); self.assertEqual(self.client.get(reverse("edit_job", args=[self.job2.id])).status_code, 404)

    def test_ranking_contains_only_owned_applications(self):
        self.login(self.r1); response = self.client.get(reverse("priority_ranking")); self.assertContains(response, "R1 Python"); self.assertNotContains(response, "R2 Django")

    def test_other_recruiter_cannot_update_application_status(self):
        self.login(self.r1); response = self.client.post(reverse("update_application_status", args=[self.app2.id]), {"status":"Rejected"}); self.assertEqual(response.status_code, 404); self.app2.refresh_from_db(); self.assertEqual(self.app2.status, "Applied")

    def test_owner_can_update_application_status(self):
        self.login(self.r1); response = self.client.post(reverse("update_application_status", args=[self.app1.id]), {"status":"Shortlisted"}); self.assertRedirects(response, reverse("priority_ranking")); self.app1.refresh_from_db(); self.assertEqual(self.app1.status, "Shortlisted")

    def test_non_recruiter_is_forbidden(self):
        self.client.force_login(self.profile.user); self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)

