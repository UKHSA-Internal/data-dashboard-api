# Generated by Django 4.2.3 on 2023-07-31 09:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0010_apitimeseries_age_apitimeseries_geography_code_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="coretimeseries",
            old_name="dt",
            new_name="date",
        ),
    ]
