from wagtail import blocks, fields

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.filters import (
    GEOGRAPHY_TYPE_FIELDS,
    DataFilter,
    ThresholdFilter,
)

MINIMUM_FILTER_ROWS_COUNT = 1


class GlobalFilterRowFilters(blocks.StreamBlock):
    geography_filters = fields.StreamBlock(
        GEOGRAPHY_TYPE_FIELDS,
        min_num=MINIMUM_FILTER_ROWS_COUNT,
    )
    threshold_filters = ThresholdFilter()
    data_filters = DataFilter()


class GlobalFilterRowBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    filters = GlobalFilterRowFilters()


class TimeRangeElement(blocks.StructBlock):
    label = blocks.CharBlock(required=False)
    date_from = blocks.DateBlock(required=False, help_text=help_texts.DATE_FROM_FIELD)
    date_to = blocks.DateBlock(required=False, help_text=help_texts.DATE_TO_FIELD)


class TimeRangeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    time_periods = blocks.ListBlock(
        child_block=TimeRangeElement(),
        help_text=help_texts.GLOBAL_FILTER_TIME_RANGE_TIME_PERIOD,
    )


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
        icon = "text"
        form_classname = "global_filter_card_form"
