from wagtail import blocks
from wagtail.fields import RichTextField

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content.blocks import ChartBlock, HeadlineNumberBlock, TrendNumberBlock
from cms.dynamic_content.components import HeadlineNumberTypes


class HeadlineNumbersRowCard(blocks.StructBlock):
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    columns = HeadlineNumberTypes(min_num=1, max_num=5)

    class Meta:
        icon = "headline_number"


class ChartWithHeadlineAndTrendCard(blocks.StructBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES)
    chart = ChartBlock()
    headline_number = HeadlineNumberBlock(required=False)
    trend_number = TrendNumberBlock(required=False)

    class Meta:
        icon = "chart_card"
