from django.contrib import admin
from .models import Skill, JobRole, LearningResource


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'level',
        'learning_order'
    )


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'skill',
        'resource_type',
        'duration'
    )