from wagtail import blocks

from cms.dynamic_content import help_texts


class FilterLinkedComponent(blocks.StructBlock):
    title_prefix = blocks.CharBlock(
        required=True,
        help_text=help_texts.FILTER_LINKED_COMPONENT_TITLE_PREFIX,
    )
