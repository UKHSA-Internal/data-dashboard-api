# Generated by Django 4.1.7 on 2023-04-28 14:06

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("topic", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="topicpage",
            name="page_description",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="\nAn optional body of text which will be rendered at the top of the page. \nThis text will be displayed after the title of the page and before any of the main content.\n",
                null=True,
            ),
        ),
    ]
