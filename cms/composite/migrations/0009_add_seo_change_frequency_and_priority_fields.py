# Generated by Django 5.0.4 on 2024-06-26 16:27

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("composite", "0008_alter_compositepage_add_wha_button_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="compositepage",
            name="seo_change_frequency",
            field=models.IntegerField(
                choices=[
                    (1, "Always"),
                    (2, "Hourly"),
                    (3, "Daily"),
                    (4, "Weekly"),
                    (5, "Monthly"),
                    (6, "Yearly"),
                    (7, "Never"),
                ],
                default=5,
                help_text="<p>This value tells search engines how often a page’s content updates, offering a hint for crawling prioritization.</p>\n<p><strong>Always</strong>: This means the page is constantly changing with important, up-to-the-minute updates. \nA subreddit index page, a stock market data page, and the index page of a major news site might use this tag.</p>\n<p><strong>Hourly</strong>: The page is updated on an hourly basis or thereabouts.\n Major news sites, weather sites, and active web forums might use this tag.</p>\n<p><strong>Daily</strong>: The page is updated with new content on average once a day. \nSmall web forums, classified ad pages, daily newspapers, and daily blogs might use this tag for their homepage.</p>\n<p><strong>Weekly</strong>: The page is updated around once a week with new content. \nProduct info pages with daily pricing information, small blogs, and website directories use this tag.</p>\n<p><strong>Monthly</strong>: The page is updated around once a month; maybe more, maybe less. \nCategory pages, evergreen guides with updated information, and FAQs often use this tag.</p>\n<p><strong>Yearly</strong>: The page is rarely updated but may receive updates once or twice a year. \nMany static pages, such as registration pages, About pages, and privacy policies, fall into this category.</p>\n<p><strong>Never</strong>: The page is never going to be updated. \nOld blog entries, old news stories, and completely static pages fall into this category. </p>",
                verbose_name="SEO change frequency",
            ),
        ),
        migrations.AddField(
            model_name="compositepage",
            name="seo_priority",
            field=models.DecimalField(
                decimal_places=1,
                default=0.5,
                help_text="\nThis value signals the importance of a page to search engines. \nAssigning accurate priority values to key pages of your site can help search engines understand \nthe structure and hierarchy of your content.\nThis must be a number between 0.1 - 1.0.\n",
                max_digits=2,
                validators=[
                    django.core.validators.MaxValueValidator(Decimal("1.0")),
                    django.core.validators.MinValueValidator(Decimal("0.1")),
                ],
                verbose_name="SEO priority",
            ),
        ),
    ]