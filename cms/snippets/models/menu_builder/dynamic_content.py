from wagtail import blocks, fields

from cms.snippets.models.menu_builder import help_texts
from cms.snippets.models.menu_builder.menu_link import MenuLink


class SecondaryLinkBlock(blocks.StreamBlock):
    secondary_link = MenuLink(required=False, help_text=help_texts.SECONDARY_LINK)


class LinkBlock(blocks.StructBlock):
    primary_link = MenuLink(required=False)
    secondary_links = SecondaryLinkBlock(
        required=False, help_text=help_texts.SECONDARY_LINKS
    )


class ColumnBlock(blocks.StructBlock):
    heading = blocks.TextBlock(required=False, help_text=help_texts.MENU_COLUMN_HEADING)
    links = LinkBlock(help_text=help_texts.MENU_COLUMN_LINKS)

    class Meta:
        icon = "openquote"


class Column(blocks.StreamBlock):
    column = ColumnBlock()


class Row(blocks.StructBlock):
    columns = Column(help_text=help_texts.MENU_COLUMNS)

    class Meta:
        icon = "bars"


ALLOWABLE_BODY_CONTENT = fields.StreamField(
    block_types=[("row", Row())],
    use_json_field=True,
    help_text=help_texts.MENU_ROW,
)
