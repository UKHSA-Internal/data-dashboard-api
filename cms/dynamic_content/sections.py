from django.core.exceptions import ValidationError
from wagtail.blocks import (
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)

from cms.dynamic_content import blocks, cards, help_texts
from cms.dynamic_content.global_filter.card import GlobalFilterCard
from cms.dynamic_content.global_filter.components.map import FilterLinkedMap


class ContentCards(StreamBlock):
    text_card = cards.TextCard()
    chart_row_card = cards.ChartRowCard()
    headline_numbers_row_card = cards.HeadlineNumbersRowCard()
    global_filter_card = GlobalFilterCard(
        help_text=help_texts.GLOBAL_FILTER_COMPONENT,
    )
    filter_linked_map = FilterLinkedMap(
        required=False,
        help_text=help_texts.FILTER_LINKED_MAP_COMPONENT,
    )

    def clean(self, value):
        self._validate_dependant_blocks(value=value)
        return super().clean(value)

    @classmethod
    def _validate_dependant_blocks(cls, *, value) -> None:
        has_global_filter = any(
            block.block_type == "global_filter_card" for block in value
        )
        has_filter_linked_map = any(
            block.block_type == "filter_linked_map" for block in value
        )

        if has_filter_linked_map and not has_global_filter:
            message = "The 'Filter linked map' is only available when using 'global filter card'."
            raise ValidationError(message)


class ContentCardsSectionWithLink(StreamBlock):
    text_card = cards.TextCard()
    chart_card_section = cards.ChartCardSection()
    headline_numbers_row_card = cards.HeadlineNumbersRowCard()
    weather_health_alert_card = cards.WeatherHealthAlertsCard()


class Section(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    content = ContentCards(help_text=help_texts.CONTENT_ROW_CARDS)

    class Meta:
        icon = "thumbtack"


class SectionWithLink(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    page_link = blocks.PageLinkChooserBlock(
        page_type=["composite.CompositePage"],
        required=False,
        help_text=help_texts.INDEX_PAGE_FIELD,
    )
    content = ContentCardsSectionWithLink(help_text=help_texts.CONTENT_ROW_CARDS)

    class Meta:
        icon = "thumbtack"


class TextSection(StructBlock):
    title = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    body = RichTextBlock(help_text=help_texts.REQUIRED_BODY_FIELD, required=True)


class CodeExample(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=False)
    content = blocks.CodeBlock(help_text=help_texts.CODE_EXAMPLE, required=True)

    class Meta:
        icon = "code"
