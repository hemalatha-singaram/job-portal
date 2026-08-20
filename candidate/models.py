from django.db import models
from django.contrib.auth.models import User


class CandidateProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)

    # Candidate information
    skills = models.TextField(blank=True)
    experience = models.PositiveIntegerField(default=0)
    projects = models.TextField(blank=True)

    # NLP extracted information
    keywords = models.TextField(blank=True)
    tags = models.TextField(blank=True)

    # Resume
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )

    # Text extracted from resume
    resume_text = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


class JobApplication(models.Model):

    STATUS = (
        ("Applied", "Applied"),
        ("Shortlisted", "Shortlisted"),
        ("Interview", "Interview"),
        ("Rejected", "Rejected"),
        ("Selected", "Selected"),
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        "recruiter.Job",
        on_delete=models.CASCADE
    )

    cover_letter = models.TextField()

    # ATS information
    ats_score = models.FloatField(default=0)
    matching_percentage = models.FloatField(default=0)

    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)

    applied_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Applied"
    )

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"


class Notification(models.Model):

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.user.username} - {self.title}"


class Interview(models.Model):

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE
    )

    interview_date = models.DateField()
    interview_time = models.TimeField()
    mode = models.CharField(max_length=100)
    meeting_link = models.URLField(blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.application.candidate.user.username} - "
            f"{self.application.job.title}"
        )


class Offer(models.Model):

    application = models.OneToOneField(
        JobApplication,
        on_delete=models.CASCADE
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    joining_date = models.DateField()

    offer_letter = models.FileField(
        upload_to="offers/"
    )

    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Offer - {self.application.candidate.user.username}"