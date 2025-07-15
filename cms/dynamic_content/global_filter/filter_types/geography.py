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


class GeographyFilter(blocks.StructBlock):
    geography_types = blocks.ListBlock(
        child_block=GeographyFilterElement(),
        min_num=MINIMUM_ROWS_COUNT,
        help_text=help_texts.GLOBAL_FILTERS_GEOGRAPHY_FILTER,
    )

    class Meta:
        icon = "site"

    def clean(self, value):
        list_name = "geography_types"
        field_names = ["colour", "geography_type"]
        for field_name in field_names:
            self._validate_choices_are_unique(
                field_name=field_name, choices=value[list_name]
            )

        return super().clean(value=value)

    @classmethod
    def _validate_choices_are_unique(cls, *, field_name, choices) -> None:
        choices = [item.get(field_name) for item in choices]
        if len(set(choices)) != len(choices):
            message = (
                f"{field_name} field must be unique, please review your selections."
            )
            raise ValidationError(message)
