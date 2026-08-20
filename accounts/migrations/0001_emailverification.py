from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def mark_existing_users_verified(apps, schema_editor):
    User = apps.get_model("auth", "User")
    EmailVerification = apps.get_model("accounts", "EmailVerification")
    now = timezone.now()
    for user in User.objects.all():
        EmailVerification.objects.update_or_create(
            user_id=user.pk,
            defaults={"code": "", "expires_at": None, "verified_at": now},
        )


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="EmailVerification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(blank=True, max_length=6)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="email_verification", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(mark_existing_users_verified, migrations.RunPython.noop),
    ]
