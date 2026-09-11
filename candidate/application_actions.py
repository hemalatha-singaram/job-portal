from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import CandidateProfile, JobApplication


@login_required
def delete_application(request, application_id):
    """Allow a candidate to permanently remove their own job application."""
    if request.method != "POST":
        return redirect("applications")

    profile = get_object_or_404(CandidateProfile, user=request.user)
    application = get_object_or_404(
        JobApplication.objects.select_related("job"),
        id=application_id,
        candidate=profile,
    )

    job_title = application.job.title
    if application.resume:
        application.resume.delete(save=False)
    application.delete()

    messages.success(request, f"Your application for {job_title} was deleted successfully.")
    return redirect("applications")
