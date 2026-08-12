# Generated for the Recruiter ATS / priority-ranking features.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiter', '0002_remove_job_last_date_job_posted_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateMatch',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('overall_score', models.FloatField(default=0)),
                ('skills_score', models.FloatField(default=0)),
                ('experience_score', models.FloatField(default=0)),
                ('keyword_score', models.FloatField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('analyzed_at', models.DateTimeField(auto_now=True)),
                ('application_id', models.PositiveBigIntegerField(unique=True)),
            ],
            options={
                'ordering': ['-overall_score', '-analyzed_at'],
            },
        ),
    ]
