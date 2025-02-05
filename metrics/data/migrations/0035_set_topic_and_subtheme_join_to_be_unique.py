# Generated by Django 5.1.5 on 2025-02-05 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0034_remove_subtheme_name_unique_constraint"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="topic",
            name="`Topic` name should be unique",
        ),
        migrations.AddConstraint(
            model_name="topic",
            constraint=models.UniqueConstraint(
                fields=("name", "subtheme"),
                name="`Topic` and `SubTheme` should be a unique combination",
            ),
        ),
    ]
