from wagtail import blocks

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts
from cms.dynamic_content.blocks import HeadlineNumberBlockTypes, MetricNumberBlock
from cms.dynamic_content.components import ChartComponent, HeadlineChartComponent
from cms.metrics_interface.field_choices_callables import get_possible_axis_choices


class TextCard(blocks.StructBlock):
    body = blocks.RichTextBlock(
        features=AVAILABLE_RICH_TEXT_FEATURES, help_text=help_texts.TEXT_CARD
    )

    class Meta:
        icon = "text"


MINIMUM_HEADLINE_COLUMNS_COUNT: int = 1
MAXIMUM_HEADLINE_COLUMNS_COUNT: int = 5

MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 0
MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 2

MINIMUM_COLUMNS_CHART_COLUMNS_COUNT: int = 1
MAXIMUM_COLUMNS_CHART_COLUMNS_COUNT: int = 2


class HeadlineNumbersRowCard(blocks.StructBlock):
    columns = MetricNumberBlock(
        min_num=MINIMUM_HEADLINE_COLUMNS_COUNT,
        max_num=MAXIMUM_HEADLINE_COLUMNS_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_FIELD.format(
            MAXIMUM_HEADLINE_COLUMNS_COUNT
        ),
    )

    class Meta:
        icon = "headline_number"


class ChartWithHeadlineAndTrendCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    body = blocks.TextBlock(required=False, help_text=help_texts.OPTIONAL_BODY_FIELD)
    tag_manager_event_id = blocks.CharBlock(
        required=False,
        help_text=help_texts.TAG_MANAGER_EVENT_ID_FIELD,
        label="Tag manager event ID",
    )
    x_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_X_AXIS,
    )
    y_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_Y_AXIS,
    )
    chart = ChartComponent(help_text=help_texts.CHART_BLOCK_FIELD)
    headline_number_columns = HeadlineNumberBlockTypes(
        required=False,
        min_num=MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        max_num=MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_IN_CHART_CARD.format(
            MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT
        ),
    )

    class Meta:
        icon = "chart_with_headline_and_trend_card"


class ChartCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    body = blocks.TextBlock(required=False, help_text=help_texts.OPTIONAL_BODY_FIELD)
    tag_manager_event_id = blocks.CharBlock(
        required=False,
        help_text=help_texts.TAG_MANAGER_EVENT_ID_FIELD,
        label="Tag manager event ID",
    )
    x_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_X_AXIS,
    )
    y_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_Y_AXIS,
    )
    chart = ChartComponent(help_text=help_texts.CHART_BLOCK_FIELD)

    class Meta:
        icon = "standalone_chart"


class HeadlineChartCard(ChartCard):
    x_axis = blocks.ChoiceBlock(
        required=True,
        choices=get_possible_axis_choices,
        help_text=help_texts.REQUIRED_CHART_X_AXIS,
    )
    chart = HeadlineChartComponent(help_texts=help_texts.CHART_BLOCK_FIELD)

    class Meta:
        icon = "standalone_chart"


class ChartRowBlockTypes(blocks.StreamBlock):
    chart_card = ChartCard()
    headline_chart_card = HeadlineChartCard()
    chart_with_headline_and_trend_card = ChartWithHeadlineAndTrendCard()


class ChartRowCard(blocks.StructBlock):
    columns = ChartRowBlockTypes(
        min_num=MINIMUM_COLUMNS_CHART_COLUMNS_COUNT,
        max_num=MAXIMUM_COLUMNS_CHART_COLUMNS_COUNT,
        help_text=help_texts.CHART_CARD_ROW,
    )

    class Meta:
        icon = "chart_row_card"
