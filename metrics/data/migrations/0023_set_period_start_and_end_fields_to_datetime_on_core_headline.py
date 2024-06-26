# Generated by Django 5.0.4 on 2024-05-10 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0022_set_refresh_date_as_datetime_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coreheadline",
            name="period_end",
            field=models.DateTimeField(
                help_text="\nEnd of the period for which this figure is being provided.\n"
            ),
        ),
        migrations.AlterField(
            model_name="coreheadline",
            name="period_start",
            field=models.DateTimeField(
                help_text="\nStart of the period for which this figure is being provided.\n"
            ),
        ),
    ]
