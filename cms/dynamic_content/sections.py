from django.core.exceptions import ValidationError
from wagtail.blocks import (
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)

from cms.dynamic_content import blocks, cards, help_texts
from cms.dynamic_content.global_filter.card import GlobalFilterCard
from cms.dynamic_content.global_filter.components import (
    FilterLinkedMap,
    FilterLinkedSubPlotChartTemplate,
    FilterLinkedTimeSeriesChartTemplate,
)


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
    filter_linked_sub_plot_chart_template = FilterLinkedSubPlotChartTemplate(
        required=False,
        help_text=help_texts.FILTER_LINKED_SUB_PLOT_CHART_TEMPLATE,
    )
    filter_linked_time_series_chart_template = FilterLinkedTimeSeriesChartTemplate(
        required=False,
        help_text=help_texts.FILTER_LINKED_TIME_SERIES_CHART_TEMPLATE,
    )

    def clean(self, value):
        self._validate_dependant_blocks(value=value)
        return super().clean(value)

    def _validate_dependant_blocks(self, *, value):
        """Validate that filter-linked blocks have a global filter card.

        Raises:
            `ValidationError` - If any filter linked component blocks
                have been used without a global filter card being present.

        """
        has_global_filter = any(
            block.block_type == "global_filter_card" for block in value
        )

        if has_global_filter:
            return

        for block in value:
            if block.block_type in self._global_filter_dependent_cards:
                raise ValidationError(
                    message=self._build_filter_linked_block_error_message(block=block)
                )

    @classmethod
    def _build_filter_linked_block_error_message(cls, *, block) -> str:
        readable_block_name = block.block_type.replace("_", " ")
        return f"The '{readable_block_name}' is only available when using 'global filter card'."

    @property
    def _global_filter_dependent_cards(self) -> list[str]:
        return [
            "filter_linked_map",
            "filter_linked_sub_plot_chart_template",
            "filter_linked_time_series_chart_template",
        ]


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
