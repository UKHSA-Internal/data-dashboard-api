from wagtail.blocks import (
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)

from cms.dynamic_content import blocks, cards, help_texts


class ContentCards(StreamBlock):
    text_card = cards.TextCard()
    chart_row_card = cards.ChartRowCard()
    headline_numbers_row_card = cards.HeadlineNumbersRowCard()
    WHA_card = cards.WHACard()


class Section(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    content = ContentCards(help_text=help_texts.CONTENT_ROW_CARDS)

    class Meta:
        icon = "thumbtack"


class SectionWithLink(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    page_link = PageChooserBlock(
        page_type=["composite.CompositePage"],
        required=False,
    )
    content = ContentCards(help_text=help_texts.CONTENT_ROW_CARDS)

    class Meta:
        icon = "thumbtack"


class TextSection(StructBlock):
    title = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    body = RichTextBlock(help_text=help_texts.REQUIRED_BODY_FIELD, required=True)


class CodeExample(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=False)
    content = blocks.CodeBlock(help_text=help_texts.CODE_EXAMPLE, required=True)

    class Meta:
        icon = "code"
