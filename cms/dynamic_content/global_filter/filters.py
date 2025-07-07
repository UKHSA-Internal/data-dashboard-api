from wagtail import blocks

from cms.metrics_interface.field_choices_callables import (
    get_all_geography_names_for_ltla,
    get_all_geography_names_for_nation,
    get_all_geography_names_for_ukhsa_region,
    get_colours,
)


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
