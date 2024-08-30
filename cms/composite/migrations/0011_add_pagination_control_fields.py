# Generated by Django 5.1 on 2024-08-29 15:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("composite", "0010_add_related_links_layout_option"),
    ]

    operations = [
        migrations.AddField(
            model_name="compositepage",
            name="pagination_size",
            field=models.IntegerField(
                default=10,
                help_text="\nThis is used to control the default pagination size used if there are associated children pages.\n",
                validators=[
                    django.core.validators.MaxValueValidator(50),
                    django.core.validators.MinValueValidator(5),
                ],
            ),
        ),
        migrations.AddField(
            model_name="compositepage",
            name="show_pagination",
            field=models.BooleanField(
                default=True,
                help_text="\nThis is used to determine whether to render pagination controls or not.\n",
            ),
        ),
    ]
