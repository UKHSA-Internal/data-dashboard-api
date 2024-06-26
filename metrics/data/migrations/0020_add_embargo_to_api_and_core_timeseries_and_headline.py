# Generated by Django 4.2.6 on 2023-11-01 15:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0019_apitimeseries_record_should_be_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="apitimeseries",
            name="embargo",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="coreheadline",
            name="embargo",
            field=models.DateTimeField(
                help_text="\nThe point in time at which the data is released from embargo and made available.\n",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="coretimeseries",
            name="embargo",
            field=models.DateTimeField(
                help_text="\nThe point in time at which the data is released from embargo and made available.\n",
                null=True,
            ),
        ),
    ]
