from cms.dynamic_content.blocks import PageLinkChooserBlock
from tests.fakes.models.cms.page_link_chooser import FakePageLinkChooser
from tests.fakes.factories.cms.composite_page_factory import FakeCompositePageFactory


class TestPageLinkChooser:
    def test_page_link_chooser_returns_none(self):
        """
        Given a `PageLinkChooser` instance
        When the `PageLinkChooser.get_api_representation()` is called with
            None instead of a page link instance.
        Then None is returned.
        """
        # Given
        page_link_chooser = PageLinkChooserBlock()

        # When
        api_representation_result = page_link_chooser.get_api_representation(value=None)

        # Then
        assert api_representation_result is None
