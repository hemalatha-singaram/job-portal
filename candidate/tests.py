from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from recruiter.models import Job
from .forms import JobApplicationForm, ProfileForm
from .models import CandidateProfile, JobApplication


class CandidateIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="candidate", email="candidate@example.com", password="pass12345")
        self.profile = CandidateProfile.objects.create(user=self.user, skills="Python, Django, SQL")
        recruiter = User.objects.create_user(username="recruiter", password="pass12345")
        self.job = Job.objects.create(recruiter=recruiter, title="Python Developer", company="TestCo", location="Hyderabad", salary="₹8 LPA", job_type="Full-Time", experience="1-2 years", skills="Python, Django", description="Build APIs")

    def resume(self):
        return SimpleUploadedFile("resume.docx", b"dummy", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    def test_register_page_loads(self):
        response = self.client.get(reverse("candidate_register")); self.assertEqual(response.status_code, 200)

    def test_registration_creates_profile(self):
        response = self.client.post(reverse("candidate_register"), {"first_name":"A","last_name":"B","username":"newuser","email":"a@example.com","password":"secret123"})
        self.assertRedirects(response, reverse("candidate_login")); self.assertTrue(CandidateProfile.objects.filter(user__username="newuser").exists())

    def test_candidate_login(self):
        response = self.client.post(reverse("candidate_login"), {"username":"candidate","password":"pass12345"})
        self.assertRedirects(response, reverse("candidate_dashboard"))

    def test_job_detail_does_not_show_missing_skills_before_application(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("candidate_job_detail", args=[self.job.id]))
        self.assertEqual(response.status_code, 200); self.assertNotContains(response, "Skills you're missing")

    @patch("candidate.views.extract_resume_text_from_upload", return_value="Python Django SQL")
    def test_apply_calculates_ats_and_redirects(self, _mock):
        self.client.force_login(self.user)
        response = self.client.post(reverse("apply_job", args=[self.job.id]), {"phone":"9999999999", "qualification":"B.Tech", "resume":self.resume()})
        app = JobApplication.objects.get(candidate=self.profile, job=self.job)
        self.assertRedirects(response, reverse("ats_result", args=[app.id])); self.assertEqual(app.ats_score, 100.0); self.assertEqual(app.missing_skills, "")

    def test_profile_form_persists_education_and_experience(self):
        form = ProfileForm(instance=self.profile, data={"phone":"9999999999","address":"A","city":"Hyderabad","state":"Telangana","qualification":"B.Tech","tenth_percentage":"92","intermediate_percentage":"88","graduation_percentage":"82","graduation_cgpa":"8.4","skills":"Python","experience_level":"1-2 years","projects":"CampusHire"})
        self.assertTrue(form.is_valid()); profile = form.save(); self.assertEqual(profile.experience, 1); self.assertEqual(str(profile.graduation_cgpa), "8.40")

