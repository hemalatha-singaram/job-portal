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

    # Recruiter ATS / candidate management
    path("job/<int:job_id>/applications/", views.job_applications, name="job_applications"),
    path("job/<int:job_id>/ranked-candidates/", views.ranked_candidates, name="ranked_candidates"),
    path("application/<int:application_id>/status/", views.update_application_status, name="update_application_status"),
    path("application/<int:application_id>/note/", views.save_application_note, name="save_application_note"),
    path("application/<int:application_id>/analyze/", views.analyze_candidate, name="analyze_candidate"),
    path("application/<int:application_id>/analysis/", views.candidate_analysis, name="candidate_analysis"),
    path("job/<int:job_id>/reanalyze/", views.analyze_all_candidates, name="analyze_all_candidates"),
]
