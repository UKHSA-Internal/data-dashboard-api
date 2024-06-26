# Generated by Django 5.0.3 on 2024-03-11 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0003_externalbutton"),
    ]

    operations = [
        migrations.AlterField(
            model_name="externalbutton",
            name="button_type",
            field=models.CharField(
                choices=[
                    ("Primary", "Primary"),
                    ("Secondary", "Secondary"),
                    ("Warning", "Warning"),
                ],
                default="Primary",
                help_text="\nA required choice of the button type to be used, the options include `Primary`, `Secondary`.\nThese align with GDS guidelines.\n",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="externalbutton",
            name="icon",
            field=models.CharField(
                blank=True,
                choices=[("Download", "Download"), ("Start", "Start")],
                help_text="\nAn optional choice of icon to add to a button, defaults to none.\n",
                max_length=255,
            ),
        ),
    ]
