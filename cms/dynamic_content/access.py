from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import blocks, help_texts, sections

AVAILABLE_RICH_TEXT_FEATURES_COMPOSITE = AVAILABLE_RICH_TEXT_FEATURES[:]
CODE: str = "code"
AVAILABLE_RICH_TEXT_FEATURES_COMPOSITE.append(CODE)

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
            RichTextBlock(
                features=AVAILABLE_RICH_TEXT_FEATURES_COMPOSITE,
                help_text=help_texts.REQUIRED_BODY_FIELD,
                required=True,
            ),
        ),
        ("button", blocks.ButtonChooserBlock("snippets.button", required=False)),
        (
            "code_block",
            sections.CodeExample(
                help_texts="placeholder code block single example multiple languages possible"
            ),
        ),
    ],
    block_counts={"button": {"max_num": 1}},
    use_json_field=True,
)
