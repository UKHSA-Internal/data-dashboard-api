from unittest import mock

from cms.dynamic_content.blocks import HealthTopicSectionLink


class TestHealthTopicSectionLink:
    def test_get_api_representation_returns_none_when_value_is_none(self) -> None:
        """
        Given a `HealthTopicSectionLink`
        When `get_api_representation()` is called with `None`
        Then `None` is returned.
        """
        # Given
        block = HealthTopicSectionLink()

        # When
        api_representation_result = block.get_api_representation(value=None)

        # Then
        assert api_representation_result is None

    def test_get_api_representation_returns_heading_and_page_api_url(self) -> None:
        """
        Given a `HealthTopicSectionLink`
        When `get_api_representation()` is called with a page
        Then the returned dict includes the heading and the linked page API URL.
        """
        # Given
        block = HealthTopicSectionLink()
        fake_page = mock.Mock()
        fake_page.id = 456

        value = {
            "heading": "Health themes",
            "page": fake_page,
        }

        with mock.patch(
            "cms.dynamic_content.blocks.reverse", return_value="/api/pages/456/"
        ):
            # When
            api_representation_result = block.get_api_representation(value=value)

        # Then
        assert api_representation_result == {
            "heading": "Health themes",
            "page": "/api/pages/456/",
        }
