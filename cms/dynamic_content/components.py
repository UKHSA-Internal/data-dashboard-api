from wagtail import blocks

from cms.dynamic_content import elements, help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_subcategory_choices,
    get_all_unique_change_type_metric_names,
    get_all_unique_percent_change_type_names,
    get_colours,
)


class ChartComponent(blocks.StreamBlock):
    plot = elements.ChartPlotElement()

    class Meta:
        icon = "standalone_chart"


class HeadlineChartComponent(blocks.StreamBlock):
    plot = elements.HeadlineChartPlotElement()

    class Meta:
        icon = "standalone_chart"


class SimplifiedChartComponent(blocks.StreamBlock):
    plot = elements.SimplifiedChartPlotElement()

    class Meta:
        icon = "standalone_chart"


class DualCategoryChartStaticFieldComponent(elements.BaseMetricsElement):
    date_from = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_TO_FIELD,
    )

    class Meta:
        icon = "standalone_chart"


class DualCategoryChartSegmentComponent(blocks.StructBlock):
    secondary_field_value = blocks.ChoiceBlock(
        choices=get_all_subcategory_choices,
        help_text=help_texts.SECONDARY_FIELD_VALUES,
    )
    colour = blocks.ChoiceBlock(
        required=True,
        choices=get_colours,
        default=get_colours()[0],
        help_text=help_texts.LINE_COLOUR_FIELD,
    )
    label = blocks.TextBlock(
        required=False,
        help_text=help_texts.LABEL_FIELD,
    )

    class Meta:
        form_classname = "dual-category-chart-segments-form"
        form_template = "blocks/dual_category_segments_form.html"
        label = "Dual charts segments"


class HeadlineNumberComponent(elements.BaseMetricsElement):
    body = blocks.TextBlock(required=False, help_text=help_texts.OPTIONAL_BODY_FIELD)

    class Meta:
        icon = "bold"


class TrendNumberComponent(elements.BaseMetricsElement):
    body = blocks.TextBlock(required=False, help_text=help_texts.OPTIONAL_BODY_FIELD)
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_change_type_metric_names,
        help_text=help_texts.TREND_METRIC_FIELD,
    )
    percentage_metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_percent_change_type_names,
        help_text=help_texts.TREND_PERCENTAGE_METRIC_FIELD,
    )

    class Meta:
        icon = "arrows-up-down"


class PercentageNumberComponent(HeadlineNumberComponent):
    class Meta:
        icon = "percentage"
