from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="candidate_register"),
    path("login/", views.candidate_login, name="candidate_login"),
    path("logout/", views.candidate_logout, name="candidate_logout"),

    path("", views.dashboard, name="candidate_dashboard"),
    path("profile/", views.profile, name="candidate_profile"),
    path("jobs/", views.jobs, name="candidate_jobs"),
    path("job/<int:id>/", views.job_detail, name="candidate_job_detail"),
    path("apply/<int:id>/", views.apply_job, name="apply_job"),
    path("application/<int:application_id>/ats/", views.ats_result, name="ats_result"),
    path("applications/", views.my_applications, name="applications"),
    path("shortlisted/", views.shortlisted, name="shortlisted"),
    path("interviews/", views.interviews, name="interviews"),
    path("offers/", views.offers, name="offers"),
    path("notifications/", views.notifications, name="notifications"),
    path("analytics/", views.analytics_dashboard, name="candidate_analytics"),
    path("analytics/export/", views.analytics_export, name="analytics_export"),
]