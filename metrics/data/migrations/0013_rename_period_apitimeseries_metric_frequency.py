# Generated by Django 4.2.3 on 2023-08-02 13:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0012_rename_dt_apitimeseries_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="apitimeseries",
            old_name="period",
            new_name="metric_frequency",
        ),
    ]
