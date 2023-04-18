from wagtail import blocks
from wagtail.fields import RichTextField

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content.blocks import HeadlineNumberBlock, TrendNumberBlock


class SingleHeadlineNumberComponent(blocks.StructBlock):
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    headline_number = HeadlineNumberBlock()

    class Meta:
        icon = "number"


class HeadlineAndTrendNumberComponent(blocks.StructBlock):
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    headline_number = HeadlineNumberBlock()
    trend_number = TrendNumberBlock()

    class Meta:
        icon = "trend_down"


class DualHeadlineNumberComponent(blocks.StructBlock):
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    top_headline_number = HeadlineNumberBlock()
    bottom_headline_number = HeadlineNumberBlock()

    class Meta:
        icon = "order"


class HeadlineNumberTypes(blocks.StreamBlock):
    single_headline_component = SingleHeadlineNumberComponent()
    headline_and_trend_component = HeadlineAndTrendNumberComponent()
    dual_headline_component = DualHeadlineNumberComponent()
