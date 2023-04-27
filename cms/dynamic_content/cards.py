from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.blocks import ChartBlock
from cms.dynamic_content.components import (
    HeadlineNumberBlockTypes,
    HeadlineNumberComponentTypes,
)

MINIMUM_HEADLINE_COLUMNS_COUNT: int = 1
MAXIMUM_HEADLINE_COLUMNS_COUNT: int = 5

MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 0
MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 2


class HeadlineNumbersRowCard(blocks.StructBlock):
    columns = HeadlineNumberComponentTypes(
        min_num=MINIMUM_HEADLINE_COLUMNS_COUNT,
        max_num=MAXIMUM_HEADLINE_COLUMNS_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_FIELD_HELP_TEXT.format(
            MAXIMUM_HEADLINE_COLUMNS_COUNT
        ),
    )

    class Meta:
        icon = "headline_number"


class ChartWithHeadlineAndTrendCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True)
    body = blocks.TextBlock(required=False)
    chart = ChartBlock(help_text=help_texts.CHART_BLOCK_FIELD_HELP_TEXT)
    headline_number_columns = HeadlineNumberBlockTypes(
        required=False,
        min_num=MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        max_num=MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_IN_CHART_CARD_HELP_TEXT.format(
            MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT
        ),
    )

    class Meta:
        icon = "chart_card"
