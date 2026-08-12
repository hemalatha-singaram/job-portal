from django import forms
from django.contrib.auth.models import User

from .models import CandidateProfile, JobApplication


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class ProfileForm(forms.ModelForm):

    class Meta:
        model = CandidateProfile

        fields = [
            'phone',
            'address',
            'city',
            'state',
            'qualification',
            'skills',
            'experience',
            'projects',
            'resume',
            'profile_image',
        ]

        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'city': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'state': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'qualification': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Example: Python, Django, SQL, HTML, CSS'
            }),

            'experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),

            'projects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your projects'
            }),

            'resume': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx'
            }),

            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')

        if resume:
            allowed_extensions = ['.pdf', '.docx']
            filename = resume.name.lower()

            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    'Only PDF and DOCX files are allowed.'
                )

            # 5 MB maximum file size
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    'Resume file size must be less than 5 MB.'
                )

        return resume


class JobApplicationForm(forms.ModelForm):

    class Meta:
        model = JobApplication

        fields = [
            'cover_letter'
        ]

        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'placeholder': 'Write your cover letter...'
            })
        }