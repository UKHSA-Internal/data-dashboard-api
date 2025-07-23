import datetime

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.constants import MINIMUM_ROWS_COUNT


class TimeRangeElement(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    date_from = blocks.DateBlock(
        required=True,
        help_text=help_texts.GLOBAL_FILTER_TIME_RANGE_DATE_FROM_FIELD,
    )
    date_to = blocks.DateBlock(
        required=True,
        help_text=help_texts.GLOBAL_FILTER_TIME_RANGE_DATE_TO_FIELD,
    )

    class Meta:
        icon = "time"

    def clean(self, value: blocks.StructValue):
        self._validate_dates_are_in_chronological_order(value=value)
        return super().clean(value=value)

    @classmethod
    def _validate_dates_are_in_chronological_order(
        cls, *, value: blocks.StructBlock
    ) -> None:
        date_from = value["date_from"]
        date_to = value["date_to"]

        if date_from >= date_to:
            block_errors = {
                "date_from": ValidationError(
                    "The `date_from` must be earlier than the `date_to`"
                ),
            }
            raise blocks.StructBlockValidationError(block_errors=block_errors)


class TimePeriods(blocks.StreamBlock):
    time_period = TimeRangeElement()


class TimeRangeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    time_periods = TimePeriods(
        help_text=help_texts.GLOBAL_FILTER_TIME_RANGE,
        min_num=MINIMUM_ROWS_COUNT,
    )

    def clean(self, value: blocks.StructValue):
        self._validate_dates_are_in_chronological_order(value=value)
        return super().clean(value=value)

    @classmethod
    def _convert_to_date_if_needed(
        cls, *, date_stamp: str | datetime.date
    ) -> datetime.date:
        try:
            return datetime.date.fromisoformat(date_stamp)
        except TypeError:
            return date_stamp

    def _validate_dates_are_in_chronological_order(
        self, *, value: blocks.StructValue
    ) -> None:
        time_periods: blocks.StreamValue = value["time_periods"]
        error_list = ErrorList()

        for current_time_period_index, current_time_period in enumerate(time_periods):
            try:
                next_time_period = time_periods[current_time_period_index + 1]
            except IndexError:
                break

            current_time_period_date_to = self._convert_to_date_if_needed(
                date_stamp=current_time_period.value["date_to"],
            )
            next_time_period_date_from = self._convert_to_date_if_needed(
                date_stamp=next_time_period.value["date_from"],
            )

            if (
                next_time_period_date_from
                != current_time_period_date_to + datetime.timedelta(days=1)
            ):
                error_list.append(
                    ValidationError(
                        f"Time period No. {current_time_period_index + 2}'s `date_from` ({next_time_period_date_from}) "
                        f"must be 1 day after time period No. {current_time_period_index + 1} `date_to`"
                        f"({current_time_period_date_to}) to maintain sequence order"
                    )
                )

        if error_list:
            raise blocks.StructBlockValidationError(
                block_errors={"time_periods": error_list}
            )
