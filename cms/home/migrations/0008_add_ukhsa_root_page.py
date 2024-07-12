# Generated by Django 5.0.6 on 2024-06-28 14:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_add_seo_change_frequency_and_priority_fields"),
        ("wagtailcore", "0093_uploadedfile"),
    ]

    operations = [
        migrations.CreateModel(
            name="UKHSARootPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
