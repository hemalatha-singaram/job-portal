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

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES
    )

    experience = models.CharField(max_length=50)
    skills = models.TextField()
    description = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CandidateMatch(models.Model):
    """
    Stores ATS analysis for a candidate's application.

    This model belongs to the Recruiter module and does not
    modify the Candidate module.
    """

    application = models.OneToOneField(
        'candidate.JobApplication',
        on_delete=models.CASCADE,
        related_name='candidate_match'
    )

    ats_score = models.FloatField(default=0)

    matched_skills = models.TextField(
        blank=True,
        default=''
    )

    missing_skills = models.TextField(
        blank=True,
        default=''
    )

    analysis = models.TextField(
        blank=True,
        default=''
    )

    analyzed_date = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.application.candidate.user.username} - "
            f"{self.application.job.title} - "
            f"{self.ats_score}%"
        )