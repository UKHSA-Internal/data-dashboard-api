from wagtail import blocks

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.metrics_interface.interface import (
    get_all_geographies,
    get_all_geography_types,
    get_all_stratums,
    get_all_topic_names,
    get_all_unique_change_percent_type_metric_names,
    get_all_unique_change_type_metric_names,
    get_all_unique_metric_names,
    get_chart_types,
)


class BaseMetricsBlock(blocks.StructBlock):
    topic = blocks.ChoiceBlock(required=True, choices=get_all_topic_names)
    metric = blocks.ChoiceBlock(required=True, choices=get_all_unique_metric_names)


class TextBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES)

    class Meta:
        icon = "text"


class ChartPlot(BaseMetricsBlock):
    chart_type = blocks.ChoiceBlock(required=True, choices=get_chart_types)
    date_from = blocks.DateBlock(required=False)
    date_to = blocks.DateBlock(required=False)
    stratum = blocks.ChoiceBlock(required=False, choices=get_all_stratums)
    geography = blocks.ChoiceBlock(required=False, choices=get_all_geographies)
    geography_type = blocks.ChoiceBlock(required=False, choices=get_all_geography_types)

    class Meta:
        icon = "chart_plot"


class ChartBlock(blocks.StreamBlock):
    plot = ChartPlot()

    class Meta:
        icon = "standalone_chart"


class ChartCard(blocks.StructBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES, required=False)
    chart = ChartBlock()

    class Meta:
        icon = "standalone_chart"


class HeadlineNumberBlock(BaseMetricsBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES, required=False)

    class Meta:
        icon = "bold"


class TrendNumberBlock(BaseMetricsBlock):
    body = blocks.RichTextBlock(features=AVAILABLE_RICH_TEXT_FEATURES, required=False)
    metric = blocks.ChoiceBlock(
        required=True, choices=get_all_unique_change_type_metric_names
    )
    percentage_metric = blocks.ChoiceBlock(
        required=True, choices=get_all_unique_change_percent_type_metric_names
    )

    class Meta:
        icon = "arrows-up-down"
