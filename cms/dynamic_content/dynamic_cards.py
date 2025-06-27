import json

from django import forms
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.telepath import register

from cms.dynamic_content import elements, help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_age_names,
    get_all_geography_names,
    get_all_sex_names,
    get_all_stratum_names,
    get_colours,
    get_dual_category_chart_types,
    get_dual_chart_secondary_category_choices,
    get_possible_axis_choices,
)

DEFAULT_SIMPLE_CHART_X_AXIS = "age"
DEFAULT_SIMPLE_CHART_Y_AXIS = "metric"

SUBCATEGORY_CHOICES_DB = {
    "age": get_all_age_names(),
    "sex": get_all_sex_names(),
    "stratum": get_all_stratum_names(),
    "geography": get_all_geography_names(),
}


def get_all_subcategory_choices() -> list[tuple[str, str]]:
    return [
        item
        for subcategories in SUBCATEGORY_CHOICES_DB.values()
        for item in subcategories
    ]


class StaticFieldBlock(elements.BaseMetricsElement):
    date_from = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_TO_FIELD,
    )


class ChartSegmentsBlock(blocks.StructBlock):
    secondary_field_value = blocks.ChoiceBlock(
        choices=get_all_subcategory_choices,
        help_text=help_texts.SECONDARY_FIELD_VALUES,
    )
    color = blocks.ChoiceBlock(
        required=True,
        choices=get_colours,
        default=get_colours()[0],
        help_text=help_texts.LINE_COLOUR_FIELD,
    )
    label = blocks.TextBlock(
        required=False,
        help_text=help_texts.LABEL_FIELD,
    )

    class Meta:
        form_classname = "dual-category-chart-segments-form"
        form_template = "blocks/dual_category_segments_form.html"
        label = "Dual charts segments"


class DualCategoryChartCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    body = blocks.TextBlock(
        required=False, help_text=help_texts.OPTIONAL_BODY_FIELD, label="Subtitle"
    )
    about = blocks.TextBlock(
        required=False, default="", help_text=help_texts.OPTIONAL_CHART_ABOUT_FIELD
    )
    tag_manager_event_id = blocks.CharBlock(
        required=False,
        help_text=help_texts.TAG_MANAGER_EVENT_ID_FIELD,
        label="Tag manager event ID",
    )
    x_axis = blocks.ChoiceBlock(
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_X_AXIS,
    )
    x_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
    )
    primary_field_values = blocks.MultipleChoiceBlock(
        choices=get_all_subcategory_choices,
        required=False,
        help_text=help_texts.PRIMARY_FIELD_VALUES,
    )
    y_axis = blocks.ChoiceBlock(
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_Y_AXIS,
    )
    y_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_Y_AXIS_TITLE,
    )
    y_axis_minimum_value = blocks.DecimalBlock(
        required=False,
        default=0,
        help_text=help_texts.CHART_Y_AXIS_MINIMUM_VALUE,
    )
    y_axis_maximum_value = blocks.DecimalBlock(
        required=False,
        help_text=help_texts.CHART_Y_AXIS_MAXIMUM_VALUE,
    )
    chart_type = blocks.ChoiceBlock(
        required=False,
        choices=get_dual_category_chart_types,
        help_text=help_texts.CHART_TYPE_FIELD,
    )

    static_fields = StaticFieldBlock()

    second_category = blocks.ChoiceBlock(
        choices=get_dual_chart_secondary_category_choices,
        help_text=help_texts.SECONDARY_CATEGORY,
    )

    segments = blocks.ListBlock(
        ChartSegmentsBlock(),
        min_num=1,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_form_context(self, value, prefix="", errors=None):
        context = super().get_form_context(value=value, prefix=prefix, errors=errors)
        context["subcategory_data"] = json.dumps(SUBCATEGORY_CHOICES_DB)

        return context

    class Meta:
        form_classname = "dual-category-chart-form"
        form_template = "blocks/dual_category_chart_form.html"
        label = "Dual Category Chart"
        icon = "standalone_chart"


class DualCategoryChartCardAdapter(StructBlockAdapter):
    """A telepath adaptor for `DualCategoryChartCard` this...

    Note:
         This adaptor attaches our customer JavaScript implementation
         `cms/dashboard/static/js/dual_category_chart_form.js`
    """

    js_constructor = "cms.dynamic_content.dynamic_cards.DualCategoryChartCard"

    @property
    def media(self):
        struct_block_media = super().media
        dual_category_chart_media = forms.Media(js=["js/dual_category_chart_form.js"])
        return struct_block_media + dual_category_chart_media


register(DualCategoryChartCardAdapter(), DualCategoryChartCard)
