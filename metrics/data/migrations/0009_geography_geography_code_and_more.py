# Generated by Django 4.2.3 on 2023-07-20 15:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0008_add_metricgroup_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="geography",
            name="geography_code",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="coreheadline",
            name="metric_value",
            field=models.DecimalField(decimal_places=4, max_digits=11),
        ),
    ]
