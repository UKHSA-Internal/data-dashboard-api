# Generated by Django 5.1.2 on 2024-11-05 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "metrics_documentation",
            "0008_remove_metricsdocumentationchildentry_date_posted",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="metricsdocumentationparentpage",
            name="date_posted",
        ),
    ]
