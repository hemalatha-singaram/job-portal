from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_emailverification")]
    operations = [migrations.DeleteModel(name="EmailVerification")]
