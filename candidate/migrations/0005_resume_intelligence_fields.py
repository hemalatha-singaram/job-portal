from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("candidate", "0004_candidateprofile_certificates"),
    ]

    operations = [
        migrations.AddField(model_name="candidateprofile", name="internships", field=models.TextField(blank=True)),
        migrations.AddField(model_name="candidateprofile", name="hackathons", field=models.TextField(blank=True)),
        migrations.AddField(model_name="candidateprofile", name="programming_languages", field=models.TextField(blank=True)),
        migrations.AddField(model_name="candidateprofile", name="tools", field=models.TextField(blank=True)),
    ]
