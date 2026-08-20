from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("candidate", "0005_resume_intelligence_fields")]
    operations = [
        migrations.AddField(
            model_name="candidateprofile", name="tenth_gpa",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
    ]
