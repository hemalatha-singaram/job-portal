from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "company", "location", "salary", "job_type", "experience", "skills", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Data Science Engineer"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company name"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Hyderabad / Remote"}),
            "salary": forms.TextInput(attrs={"class": "form-control", "placeholder": "₹8,00,000 - ₹12,00,000 PA"}),
            "job_type": forms.Select(attrs={"class": "form-select"}),
            "experience": forms.TextInput(attrs={"class": "form-control", "placeholder": "0-2 years"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Python, SQL, Machine Learning, Django"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Responsibilities, qualifications and role details..."}),
        }
