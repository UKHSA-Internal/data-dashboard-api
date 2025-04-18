from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES
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

ALLOWABLE_BODY_CONTENT_SECTION_LINK = StreamField(
    [
        ("section", sections.SectionWithLink()),
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
        (
            "code_block",
            sections.CodeExample(),
        ),
        (
            "internal_button",
            blocks.InternalButtonChooserBlock(
                "snippets.internalbutton",
                required=False,
            ),
        ),
        (
            "external_button",
            blocks.ExternalButtonChooserBlock(
                "snippets.externalbutton",
                required=False,
            ),
        ),
        (
            "wha_button",
            blocks.WhaButtonChooserBlock(
                "snippets.weatheralertbutton",
                required=False,
            ),
        ),
        (
            "internal_page_links",
            blocks.InternalPageLinks(),
        ),
    ],
    use_json_field=True,
)
