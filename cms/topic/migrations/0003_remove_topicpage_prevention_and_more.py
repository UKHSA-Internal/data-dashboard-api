# Generated by Django 4.2.3 on 2023-07-20 16:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("topic", "0002_add_page_description_field"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="topicpage",
            name="prevention",
        ),
        migrations.RemoveField(
            model_name="topicpage",
            name="surveillance_and_reporting",
        ),
        migrations.RemoveField(
            model_name="topicpage",
            name="symptoms",
        ),
        migrations.RemoveField(
            model_name="topicpage",
            name="transmission",
        ),
        migrations.RemoveField(
            model_name="topicpage",
            name="treatment",
        ),
    ]
