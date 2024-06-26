# Generated by Django 4.2.3 on 2023-07-26 10:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0009_geography_geography_code_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="apitimeseries",
            name="age",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="apitimeseries",
            name="geography_code",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="apitimeseries",
            name="metric_group",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="apitimeseries",
            name="month",
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="apitimeseries",
            name="refresh_date",
            field=models.DateField(null=True),
        ),
    ]
