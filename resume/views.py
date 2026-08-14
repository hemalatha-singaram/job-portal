from django.shortcuts import render, redirect
from .forms import ResumeForm
from .models import CandidateProfile


def upload_resume(request):

    candidate = CandidateProfile.objects.first()

    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():
            resume = form.save(commit=False)
            resume.candidate = candidate
            resume.save()

            return redirect('upload_resume')

    else:
        form = ResumeForm()

    return render(
        request,
        'resume/upload_resume.html',
        {'form': form}
    )