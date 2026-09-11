from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from candidate.models import JobApplication
from .views import recruiter_only


@recruiter_only
def delete_application(request, application_id):
    """Allow a recruiter to remove an applicant only from their own job."""
    if request.method != "POST":
        return redirect("priority_ranking")

    application = get_object_or_404(
        JobApplication.objects.select_related("job", "candidate__user"),
        id=application_id,
        job__recruiter=request.user,
    )

    candidate_name = (
        application.candidate.user.get_full_name()
        or application.candidate.user.username
    )
    job_title = application.job.title

    if application.resume:
        application.resume.delete(save=False)
    application.delete()

    messages.success(
        request,
        f"Application from {candidate_name} for {job_title} was removed successfully.",
    )
    return redirect("priority_ranking")
