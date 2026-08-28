from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    level = models.CharField(max_length=50, default="Beginner")
    learning_order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class JobRole(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill)

    def __str__(self):
        return self.name


class LearningResource(models.Model):
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="resources"
    )
    title = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=50,
        default="Course"
    )
    url = models.URLField(blank=True)
    duration = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title