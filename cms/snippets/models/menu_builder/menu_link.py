from django.core.exceptions import ValidationError
from django.db import models
from wagtail import blocks
from wagtail.blocks.struct_block import StructValue
from wagtail.models import Page

from cms.dashboard.models import UKHSAPage
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
        related_name="+",
        on_delete=models.CASCADE,
    )
    is_page_public = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text=help_texts.MENU_PUBLIC_PAGE_ACKNOWLEDGEMENT,
    )
    
    
    def clean(self, value):
        cleaned_data = super().clean(value)

        if not cleaned_data.get("is_page_public"):
            raise ValidationError({
                "is_page_public": ValidationError("Only public pages can be added to the menu. Please review the pages added and ensure you have ticked the acknowledgement to say the page is public.")
            })

        return cleaned_data



    class Meta:
        icon = "link"

    def get_prep_value(self, value: StructValue) -> dict[str, str | int]:
        """Adds the `html_url` of each page to the returned value

        Args:
            `value`: The inbound enriched `StructValue`
                containing the values associated with
                this `MenuLink` object

        Returns:
            Dict containing the keys as dictated by the `MenuLink`.
            With the addition of the injected `html_url` value
            for the selected page.

        """
        prep_value: dict[str, str | int] = super().get_prep_value(value=value)
        page: Page = value["page"]
        page: type[UKHSAPage] = page.specific
        prep_value["html_url"] = page.full_url

        return prep_value


class SimpleMenuLink(blocks.StructBlock):
    title = blocks.TextBlock(
        required=True,
        help_text=help_texts.MENU_LINK_HELP_TEXT,
    )
    page = blocks.PageChooserBlock(
        "wagtailcore.Page",
        related_name="+",
        on_delete=models.CASCADE,
    )

    class Meta:
        icon = "link"

    def get_prep_value(self, value: StructValue) -> dict[str, str | int]:
        """Adds the `html_url` of each page to the returned value

        Args:
            `value`: The inbound enriched `StructValue`
                containing the values associated with
                this `SimpleMenuLink` object

        Returns:
            Dict containing the keys as dictated by the
            `SimpleMenuLink`. With the addition of the injected
            `html_url` value for the selected page.

        """
        prep_value: dict[str, str | int] = super().get_prep_value(value=value)
        page: Page = value["page"]
        page: type[UKHSAPage] = page.specific
        prep_value["html_url"] = page.full_url

        return prep_value
