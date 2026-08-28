from django import forms


class SkillGapForm(forms.Form):

    JOB_ROLES = [
        ("Python Developer", "Python Developer"),
        ("Java Developer", "Java Developer"),
        ("Full Stack Developer", "Full Stack Developer"),
        ("Data Analyst", "Data Analyst"),
        ("Data Scientist", "Data Scientist"),
        ("Machine Learning Engineer", "Machine Learning Engineer"),
        ("Web Developer", "Web Developer"),
        ("Software Engineer", "Software Engineer"),
    ]

    job_role = forms.ChoiceField(
        choices=[("", "Select target job role")] + JOB_ROLES,
        label="Target Job Role",
        widget=forms.Select(
            attrs={
                "class": "form-control"
            }
        )
    )

    current_skills = forms.CharField(
        label="Current Skills",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Example: Python, HTML, CSS, Git",
                "rows": 6
            }
        )
    )