from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField

from cms.dynamic_content import blocks, help_texts, sections

ALLOWABLE_BODY_CONTENT = StreamField(
    [
        ("section", sections.Section()),
    ],
    use_json_field=True,
)

ALLOWABLE_BODY_CONTENT_TEXT_SECTION = StreamField(
    [
        ("section", sections.TextSection()),
    ],
    use_json_field=True,
)

ALLOWABLE_BODY_CONTENT_COMPOSITE = StreamField(
    [
        (
            "text",
            RichTextBlock(help_text=help_texts.REQUIRED_BODY_FIELD, required=True),
        ),
        ("button", blocks.ButtonChooserBlock("snippets.button", required=False)),
    ],
    block_counts={"button": {"max_num": 1}},
    use_json_field=True,
)
