# Generated by Django 5.0.4 on 2024-06-26 14:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0002_increase_url_field_length_commonpage_related_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="commonpage",
            name="seo_change_frequency",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Always"),
                    (2, "Hourly"),
                    (3, "Daily"),
                    (4, "Weekly"),
                    (5, "Monthly"),
                    (6, "Yearly"),
                    (7, "Never"),
                ],
                help_text="\nThis value tells search engines how often a page’s content updates, offering a hint for crawling prioritization.\n",
                null=True,
                verbose_name="SEO change frequency",
            ),
        ),
        migrations.AddField(
            model_name="commonpage",
            name="seo_priority",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="\nThis value signals the importance of a page to search engines. \nAssigning accurate priority values to key pages of your site can help search engines understand \nthe structure and hierarchy of your content.\nThis must be a number between 0.1 - 1.0.\n",
                max_digits=3,
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(1.0),
                    django.core.validators.MinValueValidator(0.099),
                ],
                verbose_name="SEO priority",
            ),
        ),
    ]
