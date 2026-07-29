from django import forms
from .models import Job


class JobForm(forms.ModelForm):

    class Meta:

        model = Job

        fields = [
            'title',
            'company',
            'location',
            'salary',
            'job_type',
            'experience',
            'skills',
            'description',
        ]

        widgets = {

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title'
            }),

            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),

            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Location'
            }),

            'salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Salary'
            }),

            'job_type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'experience': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Experience'
            }),

            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Required Skills'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Job Description'
            }),

        }