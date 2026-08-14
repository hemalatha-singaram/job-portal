from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0002_candidateprofile_keywords_candidateprofile_projects_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='tenth_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='intermediate_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='graduation_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='graduation_cgpa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='experience_level',
            field=models.CharField(
                choices=[
                    ('Fresher', 'Fresher'),
                    ('<1 year', '<1 year'),
                    ('1–2 years', '1–2 years'),
                    ('2–3 years', '2–3 years'),
                    ('3–5 years', '3–5 years'),
                    ('5+ years', '5+ years'),
                ],
                default='Fresher',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='cover_letter',
            field=models.TextField(blank=True, default=''),
        ),
    ]
