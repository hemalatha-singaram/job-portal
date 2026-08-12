from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='candidate_dashboard'),

    path('register/', views.register, name='candidate_register'),

    path('login/', views.candidate_login, name='candidate_login'),

    path('logout/', views.candidate_logout, name='candidate_logout'),

    path('jobs/', views.jobs, name='candidate_jobs'),

    path(
        'job/<int:id>/',
        views.job_detail,
        name='candidate_job_detail'
    ),

    path(
        'apply/<int:id>/',
        views.apply_job,
        name='apply_job'
    ),

    path(
        'applications/',
        views.my_applications,
        name='applications'
    ),

    path(
        'shortlisted/',
        views.shortlisted,
        name='shortlisted'
    ),

    path(
        'interviews/',
        views.interviews,
        name='interviews'
    ),

    path(
        'offers/',
        views.offers,
        name='offers'
    ),

    path(
        'profile/',
        views.profile,
        name='candidate_profile'
    ),

    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),
]