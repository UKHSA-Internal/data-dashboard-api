from wagtail.blocks import StreamBlock, StructBlock, TextBlock

from cms.dynamic_content import cards, help_texts


class ContentCards(StreamBlock):
    text_card = cards.TextCard()
    chart_card = cards.ChartCard()
    chart_with_headline_and_trend_card = cards.ChartWithHeadlineAndTrendCard()
    headline_numbers_row_card = cards.HeadlineNumbersRowCard()


class Section(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK_HELP_TEXT, required=True)
    content = ContentCards(help_text=help_texts.CONTENT_CARDS_HELP_TEXT)
