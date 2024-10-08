# Generated by Django 5.1 on 2024-08-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("whats_new", "0003_add_page_description_column_to_whats_new_child_entry"),
    ]

    operations = [
        migrations.AddField(
            model_name="whatsnewparentpage",
            name="related_links_layout",
            field=models.CharField(
                choices=[("Sidebar", "Sidebar"), ("Footer", "Footer")],
                default="Footer",
                help_text="\nThis dictates where the related links for this page will be positioned.\n",
                max_length=10,
                verbose_name="Layout",
            ),
        ),
    ]
