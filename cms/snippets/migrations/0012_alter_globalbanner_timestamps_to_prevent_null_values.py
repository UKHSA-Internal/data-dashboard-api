# Generated by Django 5.1.7 on 2025-03-20 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0011_add_created_on_and_updated_on_fields_to_global_banners"),
    ]

    operations = [
        migrations.AlterField(
            model_name="globalbanner",
            name="created_on",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="globalbanner",
            name="updated_on",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
