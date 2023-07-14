from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_geography_names,
    get_all_geography_type_names,
    get_all_sex_names,
    get_all_stratum_names,
    get_all_topic_names,
    get_all_unique_metric_names,
    get_chart_line_types,
    get_chart_types,
    get_colours,
)


class BaseMetricsElement(blocks.StructBlock):
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


class ChartPlotElement(BaseMetricsElement):
    chart_type = blocks.ChoiceBlock(
        required=True,
        choices=get_chart_types,
        help_text=help_texts.CHART_TYPE_FIELD_HELP_TEXT,
    )
    date_from = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_FROM_FIELD_HELP_TEXT,
    )
    date_to = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_TO_FIELD_HELP_TEXT,
    )
    stratum = blocks.ChoiceBlock(
        required=False,
        choices=get_all_stratum_names,
        help_text=help_texts.STRATUM_FIELD
    )
    geography = blocks.ChoiceBlock(
        required=False,
        choices=get_all_geography_names,
        help_text=help_texts.GEOGRAPHY_FIELD,
    )
    geography_type = blocks.ChoiceBlock(
        required=False,
        choices=get_all_geography_type_names,
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
    )
    sex = blocks.ChoiceBlock(
        required=False,
        choices=get_all_sex_names,
        help_text=help_texts.SEX_FIELD,
    )
    label = blocks.TextBlock(
        required=False,
        help_text=help_texts.LABEL_FIELD,
    )
    line_colour = blocks.ChoiceBlock(
        required=False,
        choices=get_colours,
        help_text=help_texts.LINE_COLOUR_FIELD,
    )
    line_type = blocks.ChoiceBlock(
        required=False,
        choices=get_chart_line_types,
        help_text=help_texts.LINE_TYPE_FIELD,
    )

    class Meta:
        icon = "chart_plot"
