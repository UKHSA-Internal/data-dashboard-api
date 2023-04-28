from wagtail import blocks

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts
from cms.metrics_interface.interface import (
    get_all_geographies,
    get_all_geography_types,
    get_all_stratums,
    get_all_topic_names,
    get_all_unique_change_type_metric_names,
    get_all_unique_metric_names,
    get_all_unique_percent_change_type_names,
    get_chart_types,
)


class BaseMetricsBlock(blocks.StructBlock):
    topic = blocks.ChoiceBlock(
        required=True,
        choices=get_all_topic_names,
        help_text=help_texts.TOPIC_FIELD_HELP_TEXT,
    )
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_metric_names,
        help_text=help_texts.METRIC_FIELD_HELP_TEXT,
    )


class TextBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(
        features=AVAILABLE_RICH_TEXT_FEATURES, help_text=help_texts.TEXT_BLOCK_HELP_TEXT
    )

    class Meta:
        icon = "text"


class HeadingBlock(blocks.StructBlock):
    body = blocks.TextBlock(help_text=help_texts.HEADING_BLOCK_HELP_TEXT)

    class Meta:
        icon = "title"


class ChartPlot(BaseMetricsBlock):
    chart_type = blocks.ChoiceBlock(
        required=True,
        choices=get_chart_types,
        help_text=help_texts.CHART_TYPE_FIELD_HELP_TEXT,
    )
    date_from = blocks.DateBlock(
        required=False, help_text=help_texts.DATE_FROM_FIELD_HELP_TEXT
    )
    date_to = blocks.DateBlock(
        required=False, help_text=help_texts.DATE_TO_FIELD_HELP_TEXT
    )
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
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD_HELP_TEXT)
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD_HELP_TEXT
    )
    chart = ChartBlock(help_text=help_texts.CHART_BLOCK_FIELD_HELP_TEXT)

    class Meta:
        icon = "standalone_chart"


class HeadlineNumberBlock(BaseMetricsBlock):
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD_HELP_TEXT
    )

    class Meta:
        icon = "bold"


class TrendNumberBlock(BaseMetricsBlock):
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
