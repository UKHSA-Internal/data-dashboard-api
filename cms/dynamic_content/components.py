from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.blocks import HeadlineNumberBlock, TrendNumberBlock


class SingleHeadlineNumberComponent(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    headline_number = HeadlineNumberBlock(
        help_text=help_texts.HEADLINE_BLOCK_FIELD_HELP_TEXT
    )

    class Meta:
        icon = "number"


class HeadlineAndTrendNumberComponent(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    headline_number = HeadlineNumberBlock(
        help_text=help_texts.HEADLINE_BLOCK_FIELD_HELP_TEXT
    )
    trend_number = TrendNumberBlock(help_text=help_texts.TREND_BLOCK_FIELD_HELP_TEXT)

    class Meta:
        icon = "trend_down"


class DualHeadlineNumberComponent(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    top_headline_number = HeadlineNumberBlock(
        help_text=help_texts.TOP_HEADLINE_BLOCK_FIELD_HELP_TEXT
    )
    bottom_headline_number = HeadlineNumberBlock(
        help_text=help_texts.BOTTOM_HEADLINE_BLOCK_FIELD_HELP_TEXT
    )

    class Meta:
        icon = "order"


class HeadlineNumberComponentTypes(blocks.StreamBlock):
    single_headline_component = SingleHeadlineNumberComponent(
        help_text=help_texts.SINGLE_HEADLINE_COMPONENT_HELP_TEXT
    )
    headline_and_trend_component = HeadlineAndTrendNumberComponent(
        help_text=help_texts.HEADLINE_AND_TREND_COMPONENT_HELP_TEXT
    )
    dual_headline_component = DualHeadlineNumberComponent(
        help_text=help_texts.DUAL_HEADLINE_COMPONENT_HELP_TEXT
    )


class HeadlineNumberBlockTypes(blocks.StreamBlock):
    headline_number = HeadlineNumberBlock(
        help_text=help_texts.HEADLINE_BLOCK_FIELD_HELP_TEXT
    )
    trend_number = TrendNumberBlock(help_text=help_texts.TREND_BLOCK_FIELD_HELP_TEXT)
