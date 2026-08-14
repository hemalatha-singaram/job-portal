from django.db import models
from django.contrib.auth.models import User


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Resume(models.Model):
    candidate = models.OneToOneField(
        CandidateProfile,
        on_delete=models.CASCADE
    )
    resume_file = models.FileField(upload_to='resumes/')

    def __str__(self):
        return self.candidate.name