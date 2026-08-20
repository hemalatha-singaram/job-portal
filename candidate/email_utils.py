from django.core.mail import send_mail
from django.conf import settings


def send_candidate_notification(candidate_email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [candidate_email],
        fail_silently=False,
    )