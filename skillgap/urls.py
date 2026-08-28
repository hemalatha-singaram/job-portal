from django.urls import path

from . import views


urlpatterns = [
    path("", views.skill_gap_home, name="skill_gap_home"),
]