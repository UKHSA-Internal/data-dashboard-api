# Generated by Django 5.0.4 on 2024-06-14 14:08

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("composite", "0006_alter_compositepage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="compositepage",
            name="page_description",
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
    ]
