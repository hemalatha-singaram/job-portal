from django import forms
from django.contrib.auth.models import User

from .models import CandidateProfile, JobApplication


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}))

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        if len(password) < 8:
            raise forms.ValidationError("Password must contain at least 8 characters.")
        return password

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.docx"}),
    )

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if not resume:
            raise forms.ValidationError("Please select a resume.")
        if not resume.name.lower().endswith((".pdf", ".docx")):
            raise forms.ValidationError("Only PDF and DOCX files are supported.")
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Resume must be smaller than 5 MB.")
        return resume


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = [
            "phone", "address", "city", "state", "qualification",
            "tenth_percentage", "tenth_gpa", "intermediate_percentage",
            "graduation_percentage", "graduation_cgpa",
            "skills", "experience_level", "projects", "certificates", "resume", "profile_image",
        ]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "10-digit phone number"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "qualification": forms.TextInput(attrs={"class": "form-control", "placeholder": "B.Tech CSE"}),
            "tenth_percentage": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01", "placeholder": "92.50"}),
            "tenth_gpa": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10, "step": "0.01", "placeholder": "10.00"}),
            "intermediate_percentage": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01", "placeholder": "88.00"}),
            "graduation_percentage": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01", "placeholder": "82.50"}),
            "graduation_cgpa": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10, "step": "0.01", "placeholder": "8.40"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Python, Django, SQL, HTML, CSS"}),
            "experience_level": forms.Select(attrs={"class": "form-select"}),
            "projects": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Project name — short description"}),
            "certificates": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Certification name — issuer — date"}),
            "resume": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.docx"}),
            "profile_image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume:
            if not resume.name.lower().endswith((".pdf", ".docx")):
                raise forms.ValidationError("Only PDF and DOCX files are allowed.")
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume must be smaller than 5 MB.")
        return resume

    def clean(self):
        cleaned = super().clean()
        for field in ("tenth_percentage", "intermediate_percentage", "graduation_percentage"):
            value = cleaned.get(field)
            if value is not None and not 0 <= value <= 100:
                self.add_error(field, "Enter a percentage between 0 and 100.")
        cgpa = cleaned.get("graduation_cgpa")
        if cgpa is not None and not 0 <= cgpa <= 10:
            self.add_error("graduation_cgpa", "Enter a CGPA between 0 and 10.")
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        level_to_years = {
            "Fresher": 0,
            "<1 year": 0,
            "1-2 years": 1,
            "2-3 years": 2,
            "3-5 years": 3,
            "5+ years": 5,
        }
        profile.experience = level_to_years.get(profile.experience_level, profile.experience)
        if commit:
            profile.save()
        return profile


class JobApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.docx"}),
        help_text="Your resume is parsed and scored for this job.",
    )
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    qualification = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = JobApplication
        fields = ["phone", "qualification", "resume"]

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if not resume:
            raise forms.ValidationError("Please upload your resume to apply.")
        if not resume.name.lower().endswith((".pdf", ".docx")):
            raise forms.ValidationError("Only PDF and DOCX files are allowed.")
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Resume must be smaller than 5 MB.")
        return resume
