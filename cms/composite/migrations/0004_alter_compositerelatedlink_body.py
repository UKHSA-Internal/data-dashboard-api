# Generated by Django 5.0.2 on 2024-02-20 11:35

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("composite", "0003_alter_compositepage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="compositerelatedlink",
            name="body",
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
    ]
