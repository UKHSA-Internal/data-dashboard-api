from wagtail import blocks
from wagtail.fields import RichTextField

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content.blocks import HeadlineNumberBlock, TrendNumberBlock


class SingleHeadlineNumberComponent(blocks.StructBlock):
    title = blocks.TextBlock(required=True)
    headline_number = HeadlineNumberBlock()

    class Meta:
        icon = "number"


class HeadlineAndTrendNumberComponent(blocks.StructBlock):
    title = blocks.TextBlock(required=True)
    headline_number = HeadlineNumberBlock()
    trend_number = TrendNumberBlock()

    class Meta:
        icon = "trend_down"


class DualHeadlineNumberComponent(blocks.StructBlock):
    title = blocks.TextBlock(required=True)
    top_headline_number = HeadlineNumberBlock()
    bottom_headline_number = HeadlineNumberBlock()

    class Meta:
        icon = "order"


class HeadlineNumberComponentTypes(blocks.StreamBlock):
    single_headline_component = SingleHeadlineNumberComponent()
    headline_and_trend_component = HeadlineAndTrendNumberComponent()
    dual_headline_component = DualHeadlineNumberComponent()


class HeadlineNumberBlockTypes(blocks.StreamBlock):
    headline_number = HeadlineNumberBlock()
    trend_number = TrendNumberBlock()
