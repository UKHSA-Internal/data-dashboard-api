from django.db import models
from wagtail import blocks

from cms.snippets.models.menu_builder import help_texts


class MenuLink(blocks.StructBlock):
    title = blocks.TextBlock(
        blank=True,
        null=True,
        required=True,
        max_length=50,
        help_text=help_texts.MENU_LINK_HELP_TEXT,
    )
    body = blocks.TextBlock(required=False, help_text=help_texts.MENU_LINK_BODY)
    page = blocks.PageChooserBlock(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    class Meta:
        icon = "link"
