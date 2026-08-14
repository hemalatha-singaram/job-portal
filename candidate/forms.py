from django import forms
from django.contrib.auth.models import User
from .models import CandidateProfile, JobApplication


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = [
            'phone', 'address', 'city', 'state', 'qualification',
            'tenth_percentage', 'intermediate_percentage', 'graduation_percentage', 'graduation_cgpa',
            'skills', 'experience_level', 'projects', 'resume', 'profile_image',
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'tenth_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01', 'placeholder': 'e.g. 92.50'}),
            'intermediate_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01', 'placeholder': 'e.g. 88.00'}),
            'graduation_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01', 'placeholder': 'e.g. 82.50'}),
            'graduation_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'step': '0.01', 'placeholder': 'e.g. 8.40'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Django, SQL, HTML, CSS'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'projects': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your projects'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            filename = resume.name.lower()
            if not filename.endswith(('.pdf', '.docx')):
                raise forms.ValidationError('Only PDF and DOCX files are allowed.')
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Resume file size must be less than 5 MB.')
        return resume

    def clean(self):
        cleaned = super().clean()
        for field in ('tenth_percentage', 'intermediate_percentage', 'graduation_percentage'):
            value = cleaned.get(field)
            if value is not None and not 0 <= value <= 100:
                self.add_error(field, 'Enter a percentage between 0 and 100.')
        cgpa = cleaned.get('graduation_cgpa')
        if cgpa is not None and not 0 <= cgpa <= 10:
            self.add_error('graduation_cgpa', 'Enter a CGPA between 0 and 10.')
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        levels = {
            'Fresher': 0,
            '<1 year': 0,
            '1–2 years': 1,
            '2–3 years': 2,
            '3–5 years': 3,
            '5+ years': 5,
        }
        profile.experience = levels.get(profile.experience_level, profile.experience)
        if commit:
            profile.save()
        return profile


class JobApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx'}),
        help_text='Upload your latest PDF or DOCX resume. It will be parsed for ATS scoring.'
    )
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    qualification = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = JobApplication
        fields = []

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            raise forms.ValidationError('Please upload your resume to apply.')
        if not resume.name.lower().endswith(('.pdf', '.docx')):
            raise forms.ValidationError('Only PDF and DOCX files are allowed.')
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Resume file size must be less than 5 MB.')
        return resume
