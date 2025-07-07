from wagtail import blocks, fields

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.filter_types import (
    DataFilter,
    ThresholdsFilter,
    TimeRangeBlock,
)
from cms.dynamic_content.global_filter.filters import GEOGRAPHY_TYPE_FIELDS

MINIMUM_FILTER_ROWS_COUNT = 1


class GlobalFilterRowFilters(blocks.StreamBlock):
    geography_filters = fields.StreamBlock(
        GEOGRAPHY_TYPE_FIELDS,
        min_num=MINIMUM_FILTER_ROWS_COUNT,
    )
    threshold_filters = ThresholdsFilter()
    data_filters = DataFilter()


class GlobalFilterRowBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    filters = GlobalFilterRowFilters()


class GlobalFilterCard(blocks.StructBlock):
    time_range = TimeRangeBlock(
        required=True,
        help_text=help_texts.GLOBAL_FILTER_TIME_RANGE,
    )

    rows = blocks.ListBlock(
        child_block=GlobalFilterRowBlock(),
        required=True,
        help_text=help_texts.GLOBAL_FILTER_ROWS,
        min_num=MINIMUM_FILTER_ROWS_COUNT,
    )

    class Meta:
        icon = "globe"
        form_classname = "global_filter_card_form"
