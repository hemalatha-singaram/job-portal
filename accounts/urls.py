from django.urls import path
from . import views

urlpatterns = [
    # Kept only as a safe compatibility route for old bookmarks. No OTP is generated.
    path("forgot-password/", views.forgot_password, name="forgot_password"),
]
