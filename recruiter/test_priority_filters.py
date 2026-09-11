from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from candidate.models import CandidateProfile, JobApplication
from recruiter.models import Job


class PriorityFilterRegressionTests(TestCase):
    def setUp(self):
        group, _ = Group.objects.get_or_create(name="Recruiters")
        self.recruiter = User.objects.create_user(username="filter-recruiter", password="pass12345")
        self.recruiter.groups.add(group)
        self.candidate = CandidateProfile.objects.create(
            user=User.objects.create_user(username="filter-candidate", password="pass12345"),
            skills="Python, Django",
            experience=2,
        )
        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title="Python Developer",
            company="CampusHire",
            location="Hyderabad",
            salary="8L",
            job_type="Full-Time",
            experience="1",
            skills="Python, Django",
            description="Test job",
        )
        self.high = JobApplication.objects.create(
            candidate=self.candidate,
            job=self.job,
            ats_score=82,
            matched_skills="Python, Django",
        )
        self.low = JobApplication.objects.create(
            candidate=self.candidate,
            job=self.job,
            ats_score=55,
            matched_skills="Python",
        )
        self.client.force_login(self.recruiter)

    def test_min_score_70_returns_only_70_plus(self):
        response = self.client.get(reverse("priority_ranking"), {"min_score": "70"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "82%")
        self.assertNotContains(response, "55%")
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_min_score_accepts_plus_suffix(self):
        response = self.client.get(reverse("priority_ranking"), {"min_score": "70+"})
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_invalid_score_does_not_crash(self):
        response = self.client.get(reverse("priority_ranking"), {"min_score": "not-a-number"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 2)

    def test_filters_are_applied_before_pagination(self):
        response = self.client.get(reverse("priority_ranking"), {"min_score": "70", "page": "1"})
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
