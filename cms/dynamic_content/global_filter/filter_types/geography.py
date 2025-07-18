from django.core.exceptions import ValidationError
from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.constants import MINIMUM_ROWS_COUNT
from cms.metrics_interface.field_choices_callables import (
    get_all_geography_type_names,
    get_colours,
)


class GeographyFilterElement(blocks.StructBlock):
    label = blocks.CharBlock(required=False)
    colour = blocks.ChoiceBlock(
        required=True,
        choices=get_colours,
        help_text=help_texts.GLOBAL_FILTERS_COLOUR_FIELD,
    )
    geography_type = blocks.ChoiceBlock(
        required=True,
        choices=get_all_geography_type_names,
        help_text=help_texts.GLOBAL_FILTERS_GEOGRAPHY_TYPE_FIELD,
    )

    class Meta:
        icon = "site"


class GeographyFilterElements(blocks.StreamBlock):
    geography_filter = GeographyFilterElement()


class GeographyFilter(blocks.StructBlock):
    geography_types = GeographyFilterElements(
        min_num=MINIMUM_ROWS_COUNT,
        help_text=help_texts.GLOBAL_FILTERS_GEOGRAPHY_FILTER,
    )

    class Meta:
        icon = "site"

    def clean(self, value: blocks.StructValue):
        self._validate_choices_are_unique(value=value)
        return super().clean(value=value)

    @classmethod
    def _validate_choices_are_unique(cls, *, value: blocks.StructValue) -> None:
        selected_labels = set()
        selected_colours = set()
        selected_geography_types = set()

        geography_types: blocks.StreamValue = value["geography_types"]

        for geography_type in geography_types:
            geography_type_value: blocks.StructValue = geography_type.value
            label_selection: str = geography_type_value["label"]
            colour_selection: str = geography_type_value["colour"]
            geography_type_selection: str = geography_type_value["geography_type"]

            block_errors = {}

            if label_selection in selected_labels:
                message = f"The label of `{label_selection}` has been used multiple times. This must be unique, please review your selection. "
                block_errors["label"] = ValidationError(message)

            if colour_selection in selected_colours:
                message = f"The colour of `{colour_selection}` has been used multiple times. This must be unique, please review your selection. "
                block_errors["colour"] = ValidationError(message)

            if geography_type_selection in selected_geography_types:
                message = f"The geography_type of `{geography_type_selection}` has been used multiple times. This must be unique, please review your selection. "
                block_errors["geography_type"] = ValidationError(message)

            if block_errors:
                raise blocks.StructBlockValidationError(block_errors=block_errors)

            selected_labels.add(label_selection)
            selected_colours.add(colour_selection)
            selected_geography_types.add(geography_type_selection)
