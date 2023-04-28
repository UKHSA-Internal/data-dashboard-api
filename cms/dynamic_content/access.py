from wagtail.fields import StreamField

from cms.dynamic_content import blocks, cards

ALLOWABLE_BODY_CONTENT_BLOCKS = StreamField(
    [
        ("heading", blocks.HeadingBlock()),
        ("text", blocks.TextBlock()),
        ("standalone_chart", blocks.ChartCard()),
        ("chart_with_headline_and_trend_card", cards.ChartWithHeadlineAndTrendCard()),
        ("headline_numbers_row_card", cards.HeadlineNumbersRowCard()),
    ],
    use_json_field=True,
)
