# Generated by Django 4.2.7 on 2023-12-15 16:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("metrics_documentation", "0002_metricsdocumentationchildentry"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="metricsdocumentationchildentry",
            constraint=models.UniqueConstraint(
                fields=("metric",),
                name="There can only be 1 `MetricsDocumentationChildEntry` for each `metric`",
            ),
        ),
    ]
