from django.db import migrations

def create_default_quota(apps, schema_editor):
    QuotaConfig = apps.get_model('llm_caller', 'QuotaConfig')
    if not QuotaConfig.objects.exists():
        QuotaConfig.objects.create(daily_limit=10)

def reverse_default_quota(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('llm_caller', '0002_apirequest_error'),
    ]

    operations = [
        migrations.RunPython(create_default_quota, reverse_default_quota),
    ]
