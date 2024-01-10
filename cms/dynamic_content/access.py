from wagtail.fields import StreamField

from cms.dynamic_content import sections

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
