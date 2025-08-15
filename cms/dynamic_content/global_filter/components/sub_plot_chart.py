from wagtail import blocks

from cms.dynamic_content import help_texts

from .common import FilterLinkedComponent


class FilterLinkedSubPlotChartTemplate(FilterLinkedComponent):
    legend_title = blocks.CharBlock(
        required=True,
        help_text=help_texts.FILTER_LINKED_SUB_PLOT_CHART_LEGEND_TITLE,
    )
    target_threshold = blocks.FloatBlock(
        required=False,
        help_text=help_texts.FILTER_LINKED_SUB_PLOT_CHART_TARGET_THRESHOLD,
    )
    target_threshold_label = blocks.CharBlock(
        required=False,
        help_text=help_texts.FILTER_LINKED_SUB_PLOT_CHART_TARGET_THRESHOLD_LABEL,
    )

    class Meta:
        icon = "standalone_chart"
