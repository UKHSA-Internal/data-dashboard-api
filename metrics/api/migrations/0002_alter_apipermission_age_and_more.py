# Generated by Django 5.1.5 on 2025-01-31 16:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
        ("data", "0033_remove_rounding_column_from_metric_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apipermission",
            name="age",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="age_permissions",
                to="data.age",
            ),
        ),
        migrations.AlterField(
            model_name="apipermission",
            name="geography",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="geography_permissions",
                to="data.geography",
            ),
        ),
        migrations.AlterField(
            model_name="apipermission",
            name="geography_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="geography_type_permissions",
                to="data.geographytype",
            ),
        ),
        migrations.AlterField(
            model_name="apipermission",
            name="metric",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="metric_permissions",
                to="data.metric",
            ),
        ),
        migrations.AlterField(
            model_name="apipermission",
            name="stratum",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stratum_permissions",
                to="data.stratum",
            ),
        ),
        migrations.AlterField(
            model_name="apipermission",
            name="topic",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="topic_permissions",
                to="data.topic",
            ),
        ),
    ]
