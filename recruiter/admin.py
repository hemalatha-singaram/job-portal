from django.contrib import admin

from .models import CandidateMatch, Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'location',
        'job_type',
        'posted_date',
    )
    search_fields = ('title', 'company', 'location')
    list_filter = ('job_type',)


@admin.register(CandidateMatch)
class CandidateMatchAdmin(admin.ModelAdmin):
    list_display = (
        'application_id',
        'overall_score',
        'skills_score',
        'experience_score',
        'keyword_score',
        'analyzed_at',
    )
    search_fields = ('application_id',)
