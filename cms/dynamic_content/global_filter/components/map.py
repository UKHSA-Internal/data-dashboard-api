from wagtail import blocks

from cms.dynamic_content import help_texts


class FilterLinkedMap(blocks.StructBlock):
    legend_title = blocks.CharBlock(
        required=True,
        help_text=help_texts.FILTER_LINKED_MAP_LEGEND_TITLE,
    )

    class Meta:
        icon = "globe"
