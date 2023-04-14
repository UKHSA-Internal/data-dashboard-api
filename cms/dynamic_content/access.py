from wagtail.fields import StreamField

from cms.dynamic_content import blocks, cards

ALLOWABLE_BODY_CONTENT_BLOCKS = StreamField(
    [
        ("text", blocks.TextBlock()),
        ("standalone_chart", blocks.ChartBlock()),
        ("chart_card_with_headline", cards.ChartCard()),
        ("headline_number_row_card", cards.HeadlineNumberRowCard()),
    ],
    use_json_field=True,
)
