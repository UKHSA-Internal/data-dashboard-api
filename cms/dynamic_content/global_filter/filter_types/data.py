from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.constants import (
    MAXIMUM_DATA_CATEGORIES,
    MINIMUM_ROWS_COUNT,
)
from cms.metrics_interface.field_choices_callables import (
    LIST_OF_TWO_STRING_ITEM_TUPLES,
    get_all_age_names,
    get_all_sex_names,
    get_all_stratum_names,
    get_all_theme_names,
    get_all_topic_names,
    get_all_unique_metric_names,
    get_all_unique_sub_theme_names,
    get_colours,
)


def make_parameter_field_element(
    choices: LIST_OF_TWO_STRING_ITEM_TUPLES, help_text: str
) -> blocks.StructBlock:
    return blocks.StructBlock(
        [
            ("label", blocks.CharBlock(required=True)),
            ("value", blocks.ChoiceBlock(choices=choices, required=True)),
        ],
        help_text=help_text,
    )


DATA_CATEGORIES = ("theme", "sub_theme", "topic", "metric", "sex", "age", "stratum")

DATA_PARAMETER_FIELDS = [
    (
        "theme",
        make_parameter_field_element(
            choices=get_all_theme_names,
            help_text=help_texts.THEME_FIELD,
        ),
    ),
    (
        "sub_theme",
        make_parameter_field_element(
            choices=get_all_unique_sub_theme_names,
            help_text=help_texts.SUB_THEME_FIELD,
        ),
    ),
    (
        "topic",
        make_parameter_field_element(
            choices=get_all_topic_names,
            help_text=help_texts.TOPIC_FIELD,
        ),
    ),
    (
        "stratum",
        make_parameter_field_element(
            choices=get_all_stratum_names,
            help_text=help_texts.GLOBAL_FILTERS_DATA_FILTER_STRATUM,
        ),
    ),
    (
        "metric",
        make_parameter_field_element(
            choices=get_all_unique_metric_names,
            help_text=help_texts.METRIC_FIELD,
        ),
    ),
    (
        "age",
        make_parameter_field_element(
            choices=get_all_age_names,
            help_text=help_texts.AGE_FIELD,
        ),
    ),
    (
        "sex",
        make_parameter_field_element(
            choices=get_all_sex_names,
            help_text=help_texts.SEX_FIELD,
        ),
    ),
]


class AccompanyingPoint(blocks.StructBlock):
    label_prefix = blocks.CharBlock(required=True)
    label_suffix = blocks.CharBlock(required=False)
    parameters = blocks.StreamBlock(DATA_PARAMETER_FIELDS)


class AccompanyingPoints(blocks.StreamBlock):
    accompanying_point = AccompanyingPoint(
        required=False,
        help_text=help_texts.GLOBAL_FILTERS_DATA_FILTER_ACCOMPANYING_POINTS,
    )


class DataFilterElement(blocks.StructBlock):
    label = blocks.CharBlock(
        required=True,
        help_text="",
    )
    colour = blocks.ChoiceBlock(
        choices=get_colours,
        help_text="",
    )
    parameters = blocks.StructBlock(DATA_PARAMETER_FIELDS)
    accompanying_points = AccompanyingPoints(
        help_text=help_texts.GLOBAL_FILTERS_DATA_FILTER_ACCOMPANYING_POINTS,
        required=False,
    )


class DataCategorySelectionElement(blocks.StructBlock):
    data_category = blocks.ChoiceBlock(
        choices=[(category, category) for category in DATA_CATEGORIES],
    )

    class Meta:
        icon = "form"


class DataFilters(blocks.StructBlock):
    data_filters = blocks.ListBlock(
        child_block=DataFilterElement(),
        min_num=MINIMUM_ROWS_COUNT,
        help_text=help_texts.GLOBAL_FILTERS_DATA_FILTER,
    )
    categories_to_group_by = blocks.ListBlock(
        child_block=DataCategorySelectionElement(),
        min_num=MINIMUM_ROWS_COUNT,
        max_num=MAXIMUM_DATA_CATEGORIES,
        help_text=help_texts.DATA_FILTERS_CATEGORIES_TO_GROUP_BY,
    )

    class Meta:
        icon = "sliders"
