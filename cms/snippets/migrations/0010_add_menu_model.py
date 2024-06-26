# Generated by Django 5.0.4 on 2024-06-26 08:19

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0009_add_weatheralert_button_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Menu",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            (
                                "row",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "columns",
                                            wagtail.blocks.StreamBlock(
                                                [
                                                    (
                                                        "column",
                                                        wagtail.blocks.StructBlock(
                                                            [
                                                                (
                                                                    "heading",
                                                                    wagtail.blocks.TextBlock(
                                                                        help_text="\nAn optional heading to place at the top of this menu column.\n",
                                                                        required=False,
                                                                    ),
                                                                ),
                                                                (
                                                                    "links",
                                                                    wagtail.blocks.StructBlock(
                                                                        [
                                                                            (
                                                                                "primary_link",
                                                                                wagtail.blocks.StructBlock(
                                                                                    [
                                                                                        (
                                                                                            "title",
                                                                                            wagtail.blocks.TextBlock(
                                                                                                blank=True,
                                                                                                help_text="\nThe title to display for this menu item.\nAs a general rule of thumb, the title length should be no longer than 60 characters.\n",
                                                                                                null=True,
                                                                                                required=True,
                                                                                            ),
                                                                                        ),
                                                                                        (
                                                                                            "body",
                                                                                            wagtail.blocks.RichTextBlock(
                                                                                                features=[
                                                                                                    "bold",
                                                                                                    "italic",
                                                                                                    "link",
                                                                                                ],
                                                                                                help_text="\nAn optional body of text to display for this menu item.\n",
                                                                                                required=False,
                                                                                            ),
                                                                                        ),
                                                                                        (
                                                                                            "page",
                                                                                            wagtail.blocks.PageChooserBlock(
                                                                                                "wagtailcore.Page",
                                                                                                blank=True,
                                                                                                null=True,
                                                                                                on_delete=django.db.models.deletion.CASCADE,
                                                                                                related_name="+",
                                                                                            ),
                                                                                        ),
                                                                                    ],
                                                                                    required=False,
                                                                                ),
                                                                            ),
                                                                            (
                                                                                "secondary_links",
                                                                                wagtail.blocks.StreamBlock(
                                                                                    [
                                                                                        (
                                                                                            "secondary_link",
                                                                                            wagtail.blocks.StructBlock(
                                                                                                [
                                                                                                    (
                                                                                                        "title",
                                                                                                        wagtail.blocks.TextBlock(
                                                                                                            blank=True,
                                                                                                            help_text="\nThe title to display for this menu item.\nAs a general rule of thumb, the title length should be no longer than 60 characters.\n",
                                                                                                            null=True,
                                                                                                            required=True,
                                                                                                        ),
                                                                                                    ),
                                                                                                    (
                                                                                                        "body",
                                                                                                        wagtail.blocks.RichTextBlock(
                                                                                                            features=[
                                                                                                                "bold",
                                                                                                                "italic",
                                                                                                                "link",
                                                                                                            ],
                                                                                                            help_text="\nAn optional body of text to display for this menu item.\n",
                                                                                                            required=False,
                                                                                                        ),
                                                                                                    ),
                                                                                                    (
                                                                                                        "page",
                                                                                                        wagtail.blocks.PageChooserBlock(
                                                                                                            "wagtailcore.Page",
                                                                                                            blank=True,
                                                                                                            null=True,
                                                                                                            on_delete=django.db.models.deletion.CASCADE,
                                                                                                            related_name="+",
                                                                                                        ),
                                                                                                    ),
                                                                                                ],
                                                                                                help_text="\nA secondary link to attach to the list of submenu items under the primary menu link.\n",
                                                                                                required=False,
                                                                                            ),
                                                                                        )
                                                                                    ],
                                                                                    help_text="\nOptional secondary / submenu links to attach under the primary menu link.\n",
                                                                                    required=False,
                                                                                ),
                                                                            ),
                                                                        ],
                                                                        help_text="\nAdd any number of associated links within this menu column.\n",
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                    )
                                                ],
                                                help_text="\nAdd any number of columns within this menu row.\n",
                                            ),
                                        )
                                    ]
                                ),
                            )
                        ],
                        help_text="\nThe menu is constructed from a grid system of rows and columns.\nThere can be any number of rows and columns.\nBut each column should have at least 1 link.\n",
                    ),
                ),
                (
                    "internal_label",
                    models.TextField(
                        help_text="\nA label to associate with this particular menu design.\nNote that this label is private / internal and is not used on the dashboard.\nThis is purely to help identify each of the constructed menu designs.\n"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=False,
                        help_text="\nWhether to activate this menu. \nNote that only 1 menu can be active at a time.\nTo switch from 1 active menu to another, \nyou must deactivate the 1st menu and save it before activating and saving the 2nd menu.\n",
                    ),
                ),
            ],
        ),
    ]
