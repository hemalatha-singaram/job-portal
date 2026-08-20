from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("candidate", "0003_application_resume_profile_fields")]

    operations = [
        migrations.AddField(
            model_name="candidateprofile",
            name="certificates",
            field=models.TextField(blank=True),
        ),
    ]
