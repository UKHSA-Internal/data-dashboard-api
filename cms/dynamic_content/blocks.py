from wagtail import blocks
from wagtail.blocks import BooleanBlock

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.metrics_interface.interface import (
    get_all_topic_names,
    get_all_unique_change_percent_type_metric_names,
    get_all_unique_change_type_metric_names,
    get_all_unique_metric_names,
    get_chart_types,
)


class BaseMetricsBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES, required=False)

    topic = blocks.ChoiceBlock(required=True, choices=get_all_topic_names)
    metric = blocks.ChoiceBlock(required=True, choices=get_all_unique_metric_names)


class TextBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES)

    class Meta:
        icon = "text"


class ChartBlock(BaseMetricsBlock):
    include_latest_date_of_metric = BooleanBlock(default=False)

    chart_type = blocks.ChoiceBlock(required=True, choices=get_chart_types)
    date_from = blocks.DateBlock()

    class Meta:
        icon = "standalone_chart"


class HeadlineNumberBlock(BaseMetricsBlock):
    class Meta:
        icon = "bold"


class TrendNumberBlock(BaseMetricsBlock):
    metric = blocks.ChoiceBlock(
        required=True, choices=get_all_unique_change_type_metric_names
    )
    percentage_metric = blocks.ChoiceBlock(
        required=True, choices=get_all_unique_change_percent_type_metric_names
    )

    class Meta:
        icon = "arrows-up-down"
