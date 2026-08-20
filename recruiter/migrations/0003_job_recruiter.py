from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recruiter", "0002_remove_job_last_date_job_posted_date_and_more"),
    ]

    def assign_existing_jobs(apps, schema_editor):
        Job = apps.get_model("recruiter", "Job")
        User = apps.get_model("auth", "User")
        Group = apps.get_model("auth", "Group")
        try:
            group = Group.objects.get(name="Recruiters")
        except Group.DoesNotExist:
            return
        recruiters = User.objects.filter(groups=group).distinct()
        if recruiters.count() == 1:
            Job.objects.filter(recruiter__isnull=True).update(recruiter=recruiters.first())

    operations = [
        migrations.AddField(
            model_name="job",
            name="recruiter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posted_jobs",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_existing_jobs, migrations.RunPython.noop),
    ]
