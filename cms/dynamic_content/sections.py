from wagtail.blocks import (
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)

from cms.dynamic_content import cards, help_texts

languages = [
    ("Javascript", "javascript"),
    ("Typescript", "Typescript"),
    ("Python", "Python"),
]


def get_languages():
    """Callable used to populate language choices without updating migrations when adding languages"""

    return languages


class ContentCards(StreamBlock):
    text_card = cards.TextCard()
    chart_row_card = cards.ChartRowCard()
    headline_numbers_row_card = cards.HeadlineNumbersRowCard()


class Section(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    content = ContentCards(help_text=help_texts.CONTENT_ROW_CARDS)

    class Meta:
        icon = "thumbtack"


class TextSection(StructBlock):
    title = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    body = RichTextBlock(help_text=help_texts.REQUIRED_BODY_FIELD, required=True)


class CodeSnippet(StructBlock):
    language = ChoiceBlock(choices=get_languages, default=languages[0])
    code = TextBlock(form_classname="codeblock_monospace")


class CodeBlock(StreamBlock):
    code_snippet = CodeSnippet()


class CodeExample(StructBlock):
    heading = TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    content = CodeBlock(help_text=help_texts.CODEEXAMPLE, required=True)

    class Meta:
        icon = "thumbstick"
