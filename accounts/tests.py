from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountFlowTests(TestCase):
    def test_old_forgot_password_url_never_generates_otp(self):
        User.objects.create_user(username="candidate", email="candidate@example.com", password="secret123")
        response = self.client.get(reverse("forgot_password") + "?role=student", follow=True)
        self.assertRedirects(response, reverse("candidate_login"))
        self.assertNotIn("verification code", response.content.decode().lower())
