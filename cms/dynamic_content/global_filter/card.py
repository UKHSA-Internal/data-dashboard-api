from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.constants import MINIMUM_ROWS_COUNT
from cms.dynamic_content.global_filter.filter_types import (
    DataFilters,
    GeographyFilter,
    ThresholdsFilter,
    TimeRangeBlock,
)


class GlobalFilterRowFilters(blocks.StreamBlock):
    geography_filters = GeographyFilter()
    threshold_filters = ThresholdsFilter()
    data_filters = DataFilters()


class GlobalFilterRowBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    filters = GlobalFilterRowFilters()

    class Meta:
        icon = "thumbtack-crossed"


class GlobalFilterRows(blocks.StreamBlock):
    row = GlobalFilterRowBlock()

    class Meta:
        icon = "thumbtack-crossed"


class GlobalFilterCard(blocks.StructBlock):
    time_range = TimeRangeBlock(
        required=True,
        help_text=help_texts.GLOBAL_FILTER_TIME_RANGE,
    )

    rows = GlobalFilterRows(
        required=True,
        help_text=help_texts.GLOBAL_FILTER_ROWS,
        min_num=MINIMUM_ROWS_COUNT,
    )

    class Meta:
        icon = "globe"
        form_classname = "global_filter_card_form"
