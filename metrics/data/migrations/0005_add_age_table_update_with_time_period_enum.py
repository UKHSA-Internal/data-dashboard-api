# Generated by Django 4.1.9 on 2023-06-30 14:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0004_apitimeseries_coretimeseries_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Age",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name="coretimeseries",
            name="period",
            field=models.CharField(
                choices=[
                    ("A", "A"),
                    ("Q", "Q"),
                    ("M", "M"),
                    ("F", "F"),
                    ("W", "W"),
                    ("D", "D"),
                ],
                max_length=1,
            ),
        ),
    ]
