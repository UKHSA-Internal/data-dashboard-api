from wagtail import blocks

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts

from .common import FilterLinkedComponent

COVER_CHART_DATE_PREFIX_DEFAULT_TEXT = "Last updated"

class FilterLinkedTimeSeriesChartTemplate(FilterLinkedComponent):
    date_prefix = blocks.CharBlock(
        requried=True,
        default=COVER_CHART_DATE_PREFIX_DEFAULT_TEXT,
        help_text=help_texts.CHART_DATE_PREFIX,
    )
    legend_title = blocks.CharBlock(
        required=True,
        help_text=help_texts.FILTER_LINKED_TIME_SERIES_CHART_LEGEND_TITLE,
    )
    about = blocks.RichTextBlock(
        required=False,
        default="",
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.OPTIONAL_CHART_ABOUT_FIELD,
    )

    class Meta:
        icon = "history"
