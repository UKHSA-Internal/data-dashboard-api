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
