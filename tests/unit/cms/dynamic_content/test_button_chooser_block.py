from cms.dynamic_content.blocks import ButtonChooserBlock
from tests.fakes.models.cms.button_snippet import FakeButtonSnippet


class TestButtonChooser:
    def test_button_chooser_return_none(self):
        """
        Given a mock_target_app  and a `ButtonChooserBlock()` instance
        When the `ButtonChooserBlock.get_api_representation()` is called with
            None instead of a snippet instance
        Then None is returned.
        """
        # Given
        mock_target_model = "snippets.button"
        button_chooser_block = ButtonChooserBlock(target_model=mock_target_model)

        # Then
        api_representation_result = button_chooser_block.get_api_representation(
            value=None
        )

        # Then
        assert api_representation_result is None

    def test_button_chooser_returns_expected_result(self):
        """
        Given `mock_target_app`, mock data and a `ButtonChooserBlock()` instance
        When the `ButtonChooserBlock.get_api_representation()` is called with
            a `FakeSnippet()` instance
        Then `get_api_representation()` method will return the snippet instance fields
            mock_snippet_data.
        """
        # Given
        mock_target_model = "snippets.button"
        mock_snippet_data = {
            "text": "download",
            "loading_text": "downloading...",
            "endpoint": "/api/path",
            "method": "POST",
            "button_type": "DOWNLOAD",
        }
        snippet_instance = FakeButtonSnippet(**mock_snippet_data)
        button_chooser_block = ButtonChooserBlock(target_model=mock_target_model)

        # When
        api_representation = button_chooser_block.get_api_representation(
            snippet_instance
        )
        # Then
        assert api_representation == mock_snippet_data
