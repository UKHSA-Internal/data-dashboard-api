import datetime

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks

from cms.dynamic_content import help_texts


class TimeRangeElement(blocks.StructBlock):
    label = blocks.CharBlock(required=False)
    date_from = blocks.DateBlock(required=False, help_text=help_texts.DATE_FROM_FIELD)
    date_to = blocks.DateBlock(required=False, help_text=help_texts.DATE_TO_FIELD)

    def clean(self, value):
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


class TimeRangeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    time_periods = blocks.ListBlock(
        child_block=TimeRangeElement(), help_text=help_texts.GLOBAL_FILTER_TIME_RANGE
    )

    def clean(self, value):
        self._validate_dates_are_in_chronological_order(value=value)
        return super().clean(value=value)

    @classmethod
    def _validate_dates_are_in_chronological_order(
        cls, *, value: blocks.StructBlock
    ) -> None:
        time_periods = value["time_periods"]
        error_list = ErrorList()

        for current_time_period_index, current_time_period in enumerate(time_periods):
            try:
                next_time_period = time_periods[current_time_period_index + 1]
            except IndexError:
                break

            current_time_period_date_to = datetime.date.fromisoformat(
                current_time_period["date_to"]
            )
            next_time_period_date_from = datetime.date.fromisoformat(
                next_time_period["date_from"]
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
