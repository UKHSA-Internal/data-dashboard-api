from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_age_names,
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

DEFAULT_GEOGRAPHY = "England"
DEFAULT_GEOGRAPHY_TYPE = "Nation"
DEFAULT_SEX = "all"
DEFAULT_AGE = "all"
DEFAULT_STRATUM = "default"


class BaseMetricsElement(blocks.StructBlock):
    topic = blocks.ChoiceBlock(
        required=True,
        choices=get_all_topic_names,
        help_text=help_texts.TOPIC_FIELD,
    )
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_metric_names,
        help_text=help_texts.METRIC_FIELD,
    )
    geography = blocks.ChoiceBlock(
        required=True,
        choices=get_all_geography_names,
        default=DEFAULT_GEOGRAPHY,
        help_text=help_texts.GEOGRAPHY_FIELD,
    )
    geography_type = blocks.ChoiceBlock(
        required=True,
        choices=get_all_geography_type_names,
        default=DEFAULT_GEOGRAPHY_TYPE,
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
    )
    sex = blocks.ChoiceBlock(
        required=True,
        choices=get_all_sex_names,
        default=DEFAULT_SEX,
        help_text=help_texts.SEX_FIELD,
    )
    age = blocks.ChoiceBlock(
        required=True,
        choices=get_all_age_names,
        default=DEFAULT_AGE,
        help_text=help_texts.AGE_FIELD,
    )
    stratum = blocks.ChoiceBlock(
        required=True,
        choices=get_all_stratum_names,
        default=DEFAULT_STRATUM,
        help_text=help_texts.STRATUM_FIELD,
    )


class ChartPlotElement(BaseMetricsElement):
    chart_type = blocks.ChoiceBlock(
        required=True,
        choices=get_chart_types,
        help_text=help_texts.CHART_TYPE_FIELD,
    )
    date_from = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_TO_FIELD,
    )
    label = blocks.TextBlock(
        required=False,
        help_text=help_texts.LABEL_FIELD,
    )
    line_colour = blocks.ChoiceBlock(
        required=True,
        choices=get_colours,
        default=get_colours()[0],
        help_text=help_texts.LINE_COLOUR_FIELD,
    )
    line_type = blocks.ChoiceBlock(
        required=False,
        choices=get_chart_line_types,
        help_text=help_texts.LINE_TYPE_FIELD,
    )

    class Meta:
        icon = "chart_plot"
