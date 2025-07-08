from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.constants import MINIMUM_ROWS_COUNT
from cms.metrics_interface.field_choices_callables import get_colours


class ThresholdFilterElement(blocks.StructBlock):
    colour = blocks.ChoiceBlock(
        choices=get_colours,
        help_text=help_texts.GLOBAL_FILTERS_THRESHOLD_COLOR,
    )
    label = blocks.CharBlock(required=True)
    boundary_minimum_value = blocks.DecimalBlock(
        required=True,
        help_text=help_texts.GLOBAL_FILTERS_THRESHOLD_BOUNDARY_VALUE,
    )
    boundary_maximum_value = blocks.DecimalBlock(
        required=True,
        help_text=help_texts.GLOBAL_FILTERS_THRESHOLD_BOUNDARY_VALUE,
    )

    def clean(self, value):
        self._validate_boundary_minimum_value_is_lower_than_maximum_value(value=value)
        return super().clean(value=value)

    @classmethod
    def _validate_boundary_minimum_value_is_lower_than_maximum_value(
        cls, *, value: blocks.StructBlock
    ) -> None:
        minimum_value = float(value["boundary_minimum_value"])
        maximum_value = float(value["boundary_maximum_value"])

        if minimum_value >= maximum_value:
            block_errors = {
                "boundary_minimum_value": ValidationError(
                    "The `boundary_minimum_value` must be less than the `boundary_maximum_value`"
                ),
                "boundary_maximum_value": ValidationError(
                    "The `boundary_maximum_value` must be greater than the `boundary_minimum_value`"
                ),
            }
            raise blocks.StructBlockValidationError(block_errors=block_errors)


class ThresholdsFilter(blocks.StructBlock):
    thresholds = blocks.ListBlock(
        child_block=ThresholdFilterElement(),
        min_num=MINIMUM_ROWS_COUNT,
        help_text=help_texts.GLOBAL_FILTERS_THRESHOLD_FILTER,
    )

    def clean(self, value):
        self._validate_thresholds_are_in_sequence(value=value)
        return super().clean(value=value)

    @classmethod
    def _validate_thresholds_are_in_sequence(cls, *, value: blocks.StructBlock) -> None:
        thresholds = value["thresholds"]

        error_list = ErrorList()

        for current_threshold_index, current_threshold in enumerate(thresholds):
            try:
                next_threshold = thresholds[current_threshold_index + 1]
            except IndexError:
                break

            current_boundary_maximum_value = float(
                current_threshold["boundary_maximum_value"]
            )
            next_boundary_minimum_value = float(
                next_threshold["boundary_minimum_value"]
            )

            if next_boundary_minimum_value <= current_boundary_maximum_value:
                error_list.append(
                    ValidationError(
                        f"Threshold No. {current_threshold_index + 1}'s maximum value ({current_boundary_maximum_value}) must be less than "
                        f"threshold No. {current_threshold_index + 2}'s minimum value ({next_boundary_minimum_value}) to maintain sequence order"
                    )
                )

        if error_list:
            raise blocks.StructBlockValidationError(
                block_errors={"thresholds": error_list}
            )
