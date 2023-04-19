from typing import List, Tuple

from wagtail import blocks
from wagtail.blocks import BooleanBlock

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.metrics_interface import MetricsAPIInterface


def _build_choices(choices: List[str]) -> List[Tuple[str, str]]:
    return [(choice, choice) for choice in choices]


class BaseMetricsBlock(blocks.StructBlock):
    _metrics_api_interface = MetricsAPIInterface()

    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES, required=False)
    topic_names = _metrics_api_interface.get_all_topic_names()
    metric_names = _metrics_api_interface.get_all_unique_metric_names()

    topic = blocks.ChoiceBlock(required=True, choices=_build_choices(topic_names))
    metric = blocks.ChoiceBlock(required=True, choices=_build_choices(metric_names))


class TextBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES)

    class Meta:
        icon = "text"


class ChartBlock(BaseMetricsBlock):
    include_latest_date_of_metric = BooleanBlock(default=False)

    chart_types = ["simple_line_graph", "line_with_shaded_section", "waffle"]
    chart_type = blocks.ChoiceBlock(required=True, choices=_build_choices(chart_types))
    date_from = blocks.DateBlock()

    class Meta:
        icon = "standalone_chart"


class HeadlineNumberBlock(BaseMetricsBlock):
    class Meta:
        icon = "bold"


class TrendNumberBlock(BaseMetricsBlock):
    _metrics_api_interface = MetricsAPIInterface()

    metric_names = _metrics_api_interface.get_all_unique_change_type_names()
    metric = blocks.ChoiceBlock(required=True, choices=_build_choices(metric_names))

    percentage_metric_names = (
        _metrics_api_interface.get_all_unique_change_percent_type_names()
    )
    percentage_metric = blocks.ChoiceBlock(
        required=True, choices=_build_choices(percentage_metric_names)
    )

    class Meta:
        icon = "arrows-up-down"
