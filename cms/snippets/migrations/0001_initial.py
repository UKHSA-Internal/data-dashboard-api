# Generated by Django 4.2.7 on 2024-01-15 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Button",
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
                ("text", models.CharField(max_length=255)),
                ("loading_text", models.CharField(blank=True, max_length=255)),
                ("endpoint", models.CharField(blank=True, max_length=255)),
                (
                    "method",
                    models.CharField(
                        choices=[("POST", "Post"), ("GET", "Get")],
                        default="POST",
                        max_length=255,
                    ),
                ),
                (
                    "button_type",
                    models.CharField(
                        choices=[("DOWNLOAD", "Download"), ("SUBMIT", "Submit")],
                        default="DOWNLOAD",
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="button",
            constraint=models.UniqueConstraint(
                fields=("text", "button_type"),
                name="text and button type combinations should be unique",
            ),
        ),
    ]
