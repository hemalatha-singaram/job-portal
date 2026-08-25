from django.urls import path
from . import views
from . import analytics

urlpatterns = [

    path("register/", views.register, name="recruiter_register"),
    path("login/", views.recruiter_login, name="recruiter_login"),
    path("logout/", views.recruiter_logout, name="recruiter_logout"),

    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("notifications/", views.recruiter_notifications, name="recruiter_notifications"),

    path("post-job/", views.post_job, name="post_job"),

    path("jobs/", views.view_jobs, name="view_jobs"),

    path("job/<int:job_id>/", views.job_details, name="job_details"),

    path("ats-dashboard/", views.priority_ranking, name="priority_ranking"),
    path("analytics/", analytics.analytics_dashboard, name="recruiter_analytics"),
    path("analytics/export/", analytics.analytics_export, name="recruiter_analytics_export"),
    path("application/<int:application_id>/schedule-interview/", views.schedule_interview, name="schedule_interview"),
    path("application/<int:application_id>/create-offer/", views.create_offer, name="create_offer"),
    path("application/<int:application_id>/update-status/", views.update_application_status, name="update_application_status"),

    path("edit/<int:job_id>/", views.edit_job, name="edit_job"),

    path("delete/<int:job_id>/", views.delete_job, name="delete_job"),

]
