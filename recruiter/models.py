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