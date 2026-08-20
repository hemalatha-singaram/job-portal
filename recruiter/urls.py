from django.urls import path
from . import views

urlpatterns = [

    path("register/", views.register, name="recruiter_register"),
    path("login/", views.recruiter_login, name="recruiter_login"),
    path("logout/", views.recruiter_logout, name="recruiter_logout"),

    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),

    path("post-job/", views.post_job, name="post_job"),

    path("jobs/", views.view_jobs, name="view_jobs"),

    path("job/<int:job_id>/", views.job_details, name="job_details"),

    path("edit/<int:job_id>/", views.edit_job, name="edit_job"),

    path("delete/<int:job_id>/", views.delete_job, name="delete_job"),

    path("applications/", views.applications, name="recruiter_applications"),

    path("applications/<int:application_id>/schedule/", views.schedule_interview, name="schedule_interview"),

    path("applications/<int:application_id>/cancel-interview/", views.cancel_interview, name="cancel_interview"),

]
