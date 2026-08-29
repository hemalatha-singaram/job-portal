from django.shortcuts import render

from .forms import SkillGapForm
from .services import analyze_skills


def skill_gap_home(request):

    if request.method == "POST":

        form = SkillGapForm(request.POST)

        if form.is_valid():

            job_role = form.cleaned_data["job_role"]
            current_skills = form.cleaned_data["current_skills"]

            result = analyze_skills(
                job_role,
                current_skills
            )

            return render(
                request,
                "skillgap/result.html",
                {
                    "result": result
                }
            )

    else:
        form = SkillGapForm()

    return render(
        request,
        "skillgap/home.html",
        {
            "form": form
        }
    )