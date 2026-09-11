from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .ai_learning_path import generate_learning_path
from .models import JobApplication


@login_required
def learning_path(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related("job", "candidate"),
        id=application_id,
        candidate__user=request.user,
    )

    missing_skills = [
        skill.strip()
        for skill in application.missing_skills.replace(";", ",").split(",")
        if skill.strip()
    ]
    current_skills = [
        skill.strip()
        for skill in application.matched_skills.replace(";", ",").split(",")
        if skill.strip()
    ]

    path = generate_learning_path(
        application.job.title,
        missing_skills,
        current_skills=current_skills,
    )
    return JsonResponse({
        "job_role": application.job.title,
        "missing_skills": missing_skills,
        "learning_path": path,
    })
