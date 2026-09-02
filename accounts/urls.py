from django.urls import path
from . import views

urlpatterns = [
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-code/", views.verify_reset_code, name="verify_reset_code"),
    path("set-password/", views.set_new_password, name="set_new_password"),
]
