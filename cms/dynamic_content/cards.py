from wagtail import blocks

from cms.dynamic_content.blocks import ChartBlock
from cms.dynamic_content.components import (
    HeadlineNumberBlockTypes,
    HeadlineNumberComponentTypes,
)


class HeadlineNumbersRowCard(blocks.StructBlock):
    columns = HeadlineNumberComponentTypes(min_num=1, max_num=5)

    class Meta:
        icon = "headline_number"


class ChartWithHeadlineAndTrendCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True)
    body = blocks.TextBlock(required=False)
    chart = ChartBlock()
    headline_number_columns = HeadlineNumberBlockTypes(
        min_num=0, max_num=2, required=False
    )

    class Meta:
        icon = "chart_card"
