from django.db import models


class Job(models.Model):

    JOB_TYPES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Internship', 'Internship'),
        ('Remote', 'Remote'),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=50)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience = models.CharField(max_length=50)
    skills = models.TextField()
    description = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CandidateMatch(models.Model):
    """Recruiter-owned ATS analysis data for a candidate's job application."""

    # Stores the Candidate JobApplication primary key without creating a
    # migration dependency on the team's Candidate module.
    application_id = models.PositiveBigIntegerField(unique=True)
    overall_score = models.FloatField(default=0)
    skills_score = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    keyword_score = models.FloatField(default=0)
    notes = models.TextField(blank=True)
    analyzed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-overall_score', '-analyzed_at']

    def __str__(self):
        return f"Application #{self.application_id} - {self.overall_score:.0f}%"
