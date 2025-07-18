from wagtail import blocks

from cms.dynamic_content import help_texts

from .common import FilterLinkedComponent


class FilterLinkedMap(FilterLinkedComponent):
    legend_title = blocks.CharBlock(
        required=True,
        help_text=help_texts.FILTER_LINKED_MAP_LEGEND_TITLE,
    )

    class Meta:
        icon = "site"
