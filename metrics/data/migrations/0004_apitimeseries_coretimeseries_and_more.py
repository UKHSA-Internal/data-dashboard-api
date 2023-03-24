# Generated by Django 4.1.7 on 2023-03-24 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0003_increase_char_field_max_constraints"),
    ]

    operations = [
        migrations.CreateModel(
            name="APITimeSeries",
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
                ("period", models.CharField(max_length=1)),
                ("theme", models.CharField(max_length=50)),
                ("sub_theme", models.CharField(max_length=50)),
                ("topic", models.CharField(max_length=50)),
                ("geography_type", models.CharField(max_length=50)),
                ("geography", models.CharField(max_length=50)),
                ("metric", models.CharField(max_length=50)),
                ("stratum", models.CharField(max_length=50)),
                ("sex", models.CharField(max_length=3, null=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("epiweek", models.PositiveSmallIntegerField()),
                ("dt", models.DateField()),
                ("metric_value", models.FloatField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="CoreTimeSeries",
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
                (
                    "period",
                    models.CharField(
                        choices=[
                            ("A", "A"),
                            ("M", "M"),
                            ("F", "F"),
                            ("W", "W"),
                            ("D", "D"),
                        ],
                        max_length=1,
                    ),
                ),
                ("sex", models.CharField(max_length=3, null=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("epiweek", models.PositiveSmallIntegerField()),
                ("dt", models.DateField()),
                ("metric_value", models.DecimalField(decimal_places=1, max_digits=11)),
                (
                    "geography",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="data.geography",
                    ),
                ),
                (
                    "metric",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="data.metric",
                    ),
                ),
                (
                    "stratum",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="data.stratum",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="timeseries",
            name="geography",
        ),
        migrations.RemoveField(
            model_name="timeseries",
            name="metric",
        ),
        migrations.RemoveField(
            model_name="timeseries",
            name="stratum",
        ),
        migrations.DeleteModel(
            name="WeeklyTimeSeries",
        ),
        migrations.DeleteModel(
            name="TimeSeries",
        ),
    ]
