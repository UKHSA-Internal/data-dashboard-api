from wagtail import blocks

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts
from cms.dynamic_content.blocks import (
    HeadlineNumberBlockTypes,
    HeadlineNumberRowBlockTypes,
)
from cms.dynamic_content.components import ChartComponent


class TextCard(blocks.StructBlock):
    body = blocks.RichTextBlock(
        features=AVAILABLE_RICH_TEXT_FEATURES, help_text=help_texts.TEXT_CARD_HELP_TEXT
    )

    class Meta:
        icon = "text"


MINIMUM_HEADLINE_COLUMNS_COUNT: int = 1
MAXIMUM_HEADLINE_COLUMNS_COUNT: int = 5

MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 0
MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 2


class HeadlineNumbersRowCard(blocks.StructBlock):
    columns = HeadlineNumberRowBlockTypes(
        min_num=MINIMUM_HEADLINE_COLUMNS_COUNT,
        max_num=MAXIMUM_HEADLINE_COLUMNS_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_FIELD_HELP_TEXT.format(
            MAXIMUM_HEADLINE_COLUMNS_COUNT
        ),
    )

    class Meta:
        icon = "headline_number"


class ChartWithHeadlineAndTrendCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD_HELP_TEXT
    )
    chart = ChartComponent(help_text=help_texts.CHART_BLOCK_FIELD_HELP_TEXT)
    headline_number_columns = HeadlineNumberBlockTypes(
        required=False,
        min_num=MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        max_num=MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_IN_CHART_CARD_HELP_TEXT.format(
            MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT
        ),
    )

    class Meta:
        icon = "chart_with_headline_and_trend_card"


class ChartCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD_HELP_TEXT
    )
    chart = ChartComponent(help_text=help_texts.CHART_BLOCK_FIELD_HELP_TEXT)

    class Meta:
        icon = "standalone_chart"
