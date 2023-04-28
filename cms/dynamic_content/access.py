from wagtail.fields import StreamField

from cms.dynamic_content import sections

ALLOWABLE_BODY_CONTENT_BLOCKS = StreamField(
    [
        ("section", sections.SectionCard()),
    ],
    use_json_field=True,
)
