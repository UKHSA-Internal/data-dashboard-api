from django.db import models
from wagtail import blocks

from cms.snippets.models.menu_builder import help_texts

BOLD: str = "bold"
ITALIC: str = "italic"
LINKS: str = "link"

AVAILABLE_RICH_TEXT_FEATURES: list[str] = [
    BOLD,
    ITALIC,
    LINKS,
]


class MenuLink(blocks.StructBlock):
    title = blocks.TextBlock(
        blank=True,
        null=True,
        required=True,
        help_text=help_texts.MENU_LINK_HELP_TEXT,
    )
    body = blocks.RichTextBlock(
        required=False,
        help_text=help_texts.MENU_LINK_BODY,
        features=AVAILABLE_RICH_TEXT_FEATURES,
    )
    page = blocks.PageChooserBlock(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    class Meta:
        icon = "link"
