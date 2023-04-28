from wagtail.blocks import StreamBlock, StructBlock, TextBlock

from cms.dynamic_content import blocks, cards, help_texts


class Sections(StreamBlock):
    text = blocks.TextBlock()
    standalone_chart = blocks.ChartCard()
    chart_with_headline_and_trend_card = cards.ChartWithHeadlineAndTrendCard()
    headline_numbers_row_card = cards.HeadlineNumbersRowCard()


class SectionCard(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK_HELP_TEXT)
    content = Sections()
