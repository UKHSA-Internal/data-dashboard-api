# Generated by Django 4.2.4 on 2023-09-25 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commonpagerelatedlink",
            name="url",
            field=models.URLField(max_length=400, verbose_name="URL"),
        ),
    ]
