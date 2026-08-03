from django.db import models
from django.contrib.auth.models import User


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    skills = models.TextField()
    experience = models.PositiveIntegerField(default=0)
    resume = models.FileField(upload_to='resumes/')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class JobApplication(models.Model):

    STATUS = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Rejected', 'Rejected'),
        ('Selected', 'Selected'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey('recruiter.Job', on_delete=models.CASCADE)
    cover_letter = models.TextField()
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Applied')

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"


class Notification(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class Interview(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    mode = models.CharField(max_length=100)
    meeting_link = models.URLField(blank=True)
    remarks = models.TextField(blank=True)


class Offer(models.Model):
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()
    offer_letter = models.FileField(upload_to='offers/')
    accepted = models.BooleanField(default=False)