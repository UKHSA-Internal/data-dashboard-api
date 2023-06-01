from wagtail import blocks

from cms.dynamic_content import elements, help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_unique_change_type_metric_names,
    get_all_unique_percent_change_type_names,
)


class ChartComponent(blocks.StreamBlock):
    plot = elements.ChartPlotElement()

    class Meta:
        icon = "standalone_chart"


class HeadlineNumberComponent(elements.BaseMetricsElement):
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD_HELP_TEXT
    )

    class Meta:
        icon = "bold"


class TrendNumberComponent(elements.BaseMetricsElement):
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD_HELP_TEXT
    )
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_change_type_metric_names,
        help_text=help_texts.TREND_METRIC_FIELD_HELP_TEXT,
    )
    percentage_metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_percent_change_type_names,
        help_text=help_texts.TREND_PERCENTAGE_METRIC_FIELD_HELP_TEXT,
    )

    class Meta:
        icon = "arrows-up-down"


class PercentageNumberComponent(HeadlineNumberComponent):
    class Meta:
        icon = "percentage"
