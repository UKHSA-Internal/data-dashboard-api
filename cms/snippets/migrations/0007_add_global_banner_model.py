# Generated by Django 5.0.4 on 2024-04-05 12:06

import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "snippets",
            "0006_data_migration_download_button_internal_button_snippet",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="GlobalBanner",
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
                    "title",
                    models.CharField(
                        help_text="\nThe title to associate with the banner. This must be provided.\n",
                        max_length=255,
                    ),
                ),
                (
                    "body",
                    wagtail.fields.RichTextField(
                        help_text="\nA body of text to be displayed by the banner. There is a limit of 255 characters for this field.\n",
                        max_length=255,
                    ),
                ),
                (
                    "banner_type",
                    models.CharField(
                        choices=[
                            ("Information", "Information"),
                            ("Warning", "Warning"),
                        ],
                        default="Information",
                        help_text="\nThe type to associate with the banner. Defaults to `Information`.\n",
                        max_length=50,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=False,
                        help_text="\nWhether to activate this banner across every page in the dashboard. \nNote that only 1 global banner can be active at a time.\nTo switch from 1 active banner straight to another, \nyou must deactivate the 1st banner and save it before activating and saving the 2nd banner.\n",
                    ),
                ),
            ],
        ),
    ]