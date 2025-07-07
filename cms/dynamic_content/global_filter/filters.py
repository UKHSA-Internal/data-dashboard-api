from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_age_names,
    get_all_geography_names_for_ltla,
    get_all_geography_names_for_nation,
    get_all_geography_names_for_ukhsa_region,
    get_all_sex_names,
    get_all_stratum_names,
    get_all_sub_theme_names,
    get_all_theme_names,
    get_all_topic_names,
    get_all_unique_metric_names,
    get_colours,
)

MINIMUM_ROWS_COUNT = 1


def make_geography_filter_element(label, choices):
    return blocks.StructBlock(
        [
            ("label", blocks.CharBlock(required=True, default=label)),
            (
                "colour",
                blocks.ChoiceBlock(
                    choices=get_colours,
                    required=True,
                ),
            ),
            ("choices", blocks.MultipleChoiceBlock(choices=choices, required=True)),
        ]
    )


GEOGRAPHY_TYPE_FIELDS = [
    (
        "country",
        make_geography_filter_element("Country", get_all_geography_names_for_nation),
    ),
    (
        "region",
        make_geography_filter_element(
            "Region", get_all_geography_names_for_ukhsa_region
        ),
    ),
    (
        "local_tier_local_authority",
        make_geography_filter_element(
            "Local Authority", get_all_geography_names_for_ltla
        ),
    ),
]


def make_parameter_field_element(label, choices, help_text):
    return blocks.StructBlock(
        [
            ("label", blocks.CharBlock(default=label)),
            ("value", blocks.ChoiceBlock(choices=choices, required=True)),
        ],
        help_text=help_text,
    )


DATA_PARAMETER_FIELDS = [
    (
        "theme",
        make_parameter_field_element(
            label="theme", choices=get_all_theme_names, help_text=help_texts.THEME_FIELD
        ),
    ),
    (
        "sub_theme",
        make_parameter_field_element(
            "sub_theme", get_all_sub_theme_names, help_text=help_texts.SUB_THEME_FIELD
        ),
    ),
    (
        "topic",
        make_parameter_field_element(
            "topic", get_all_topic_names, help_text=help_texts.TOPIC_FIELD
        ),
    ),
    (
        "stratum",
        make_parameter_field_element(
            "stratum", get_all_stratum_names, help_text=help_texts.STRATUM_FIELD
        ),
    ),
    (
        "metric",
        make_parameter_field_element(
            "metric", get_all_unique_metric_names, help_text=help_texts.METRIC_FIELD
        ),
    ),
    (
        "age",
        make_parameter_field_element(
            "age", get_all_age_names, help_text=help_texts.AGE_FIELD
        ),
    ),
    (
        "sex",
        make_parameter_field_element(
            "sex", get_all_sex_names, help_text=help_texts.SEX_FIELD
        ),
    ),
]


class AccompanyingPoints(blocks.StructBlock):
    label_prefix = blocks.CharBlock(required=True)
    label_suffix = blocks.CharBlock(required=True)

    parameters = blocks.StreamBlock(DATA_PARAMETER_FIELDS)


class DataFilterElement(blocks.StructBlock):
    label = blocks.CharBlock(
        required=True,
        help_text="",
    )
    color = blocks.ChoiceBlock(
        choices=get_colours,
        help_text="",
    )
    parameters = blocks.StructBlock(DATA_PARAMETER_FIELDS)
    override_parameters = AccompanyingPoints()


class DataFilter(blocks.StructBlock):
    data_filter = blocks.ListBlock(
        child_block=DataFilterElement(),
        min_num=MINIMUM_ROWS_COUNT,
        help_text=help_texts.GLOBAL_FILTERS_DATA_FILTER,
    )


class ThresholdFilterElement(blocks.StructBlock):
    colour = blocks.ChoiceBlock(
        choices=get_colours,
        help_text=help_texts.GLOBAL_FILTERS_THRESHOLD_COLOR,
    )
    label = blocks.CharBlock(required=False)
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
        """
        Validate that thresholds are in proper sequence order.

        Each threshold's minimum value should match the previous threshold's maximum value,
        creating a continuous sequence without gaps or overlaps.

        Args:
            value: The StructBlock value containing the thresholds

        Raises:
            StructBlockValidationError: If thresholds are not in proper sequence
        """
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

            if current_boundary_maximum_value != next_boundary_minimum_value:
                error_list.append(
                    ValidationError(
                        f"Threshold No. {current_threshold_index + 1}'s maximum value ({current_boundary_maximum_value}) must equal "
                        f"threshold No. {current_threshold_index + 2}'s minimum value ({next_boundary_minimum_value}) to maintain sequence order"
                    )
                )

        if error_list:
            raise blocks.StructBlockValidationError(
                block_errors={"thresholds": error_list}
            )
