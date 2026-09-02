from django.contrib import admin

from .models import (
    CandidateProfile,
    JobApplication,
    Notification,
    Interview,
    Offer
)


admin.site.register(CandidateProfile)
admin.site.register(JobApplication)
admin.site.register(Notification)
admin.site.register(Interview)
admin.site.register(Offer)