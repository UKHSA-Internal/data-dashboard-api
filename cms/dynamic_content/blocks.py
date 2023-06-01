from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.components import HeadlineNumberComponent, TrendNumberComponent

MINIMUM_ROWS_NUMBER_BLOCK_COUNT: int = 1
MAXIMUM_ROWS_NUMBER_BLOCK_COUNT: int = 2


class HeadlineNumberBlockTypes(blocks.StreamBlock):
    headline_number = HeadlineNumberComponent(
        help_text=help_texts.HEADLINE_BLOCK_FIELD_HELP_TEXT
    )
    trend_number = TrendNumberComponent(
        help_text=help_texts.TREND_BLOCK_FIELD_HELP_TEXT
    )

    class Meta:
        icon = "bars"


class MetricNumberBlockTypes(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    rows = HeadlineNumberBlockTypes(
        required=True,
        min_num=MINIMUM_ROWS_NUMBER_BLOCK_COUNT,
        max_num=MAXIMUM_ROWS_NUMBER_BLOCK_COUNT,
        help_text=help_texts.NUMBERS_ROW_FIELD_HELP_TEXT.format(
            MAXIMUM_ROWS_NUMBER_BLOCK_COUNT
        ),
    )

    class Meta:
        icon = "table"


class MetricNumberBlock(blocks.StreamBlock):
    column = MetricNumberBlockTypes()
