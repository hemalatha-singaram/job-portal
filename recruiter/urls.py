from django.urls import path
from . import views

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),

    path("post-job/", views.post_job, name="post_job"),

    path("jobs/", views.view_jobs, name="view_jobs"),

    path("job/<int:job_id>/", views.job_details, name="job_details"),

    path("edit/<int:job_id>/", views.edit_job, name="edit_job"),

    path("delete/<int:job_id>/", views.delete_job, name="delete_job"),

]