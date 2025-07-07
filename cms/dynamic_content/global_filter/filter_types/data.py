from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.dynamic_content.global_filter.constants import MINIMUM_ROWS_COUNT
from cms.metrics_interface.field_choices_callables import (
    get_all_age_names,
    get_all_sex_names,
    get_all_stratum_names,
    get_all_sub_theme_names,
    get_all_theme_names,
    get_all_topic_names,
    get_all_unique_metric_names,
    get_colours,
)


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
    label_suffix = blocks.CharBlock(required=False)

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
