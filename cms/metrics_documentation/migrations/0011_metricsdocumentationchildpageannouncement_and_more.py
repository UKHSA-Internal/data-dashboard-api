# Generated by Django 5.1.7 on 2025-03-31 13:59

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "metrics_documentation",
            "0010_remove_metricsdocumentationparentpage_related_links_layout_and_related_links",
        ),
        (
            "whats_new",
            "0006_remove_whatsnewparentpage_related_links_layout_and_related_links",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="MetricsDocumentationChildPageAnnouncement",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
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
                (
                    "badge",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="whats_new.badge",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="announcements",
                        to="metrics_documentation.metricsdocumentationchildentry",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MetricsDocumentationParentPageAnnouncement",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
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
                (
                    "badge",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="whats_new.badge",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="announcements",
                        to="metrics_documentation.metricsdocumentationparentpage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
