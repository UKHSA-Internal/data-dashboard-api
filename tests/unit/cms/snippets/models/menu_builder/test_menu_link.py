from unittest import mock

from wagtail.blocks.struct_block import StructBlock

from cms.snippets.models.menu_builder.menu_link import MenuLink


class TestMenuLink:
    @mock.patch.object(StructBlock, "get_prep_value")
    def test_get_prep_value_includes_page_full_url(
        self, mocked_get_prep_value: mock.MagicMock
    ):
        """
        Given a block containing a page
        When `get_prep_value()` is called from
            an instance of `MenuLink`
        Then the `full_url` property is called from
            the specific page type associated with the page
        """
        # Given
        mocked_page = mock.Mock()
        block = {"title": "ABC", "body": mock.Mock(), "page": mocked_page}
        mocked_get_prep_value.return_value = block
        menu_link = MenuLink(title=block["title"], body=block["body"], page=mocked_page)

        # When
        prep_value = menu_link.get_prep_value(value=block)

        # Then
        assert prep_value["title"] == block["title"]
        assert prep_value["body"] == block["body"]
        assert prep_value["page"] == block["page"]
        assert prep_value["html_url"] == mocked_page.specific.full_url
