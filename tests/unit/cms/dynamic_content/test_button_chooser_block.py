from cms.dynamic_content.blocks import ButtonChooserBlock
from tests.fakes.models.cms.button_snippet import FakeButtonSnippet


class TestButtonChooser:
    def test_button_chooser_return_none(self):
        """
        Given a button_target_model  and a `ButtonChooserBlock()` instance
        When the `ButtonChooserBlock.get_api_representation()` is called with
            None instead of a snippet instance
        Then None is returned.
        """
        # Given
        button_target_model = "snippets.button"
        button_chooser_block = ButtonChooserBlock(target_model=button_target_model)

        # Then
        api_representation_result = button_chooser_block.get_api_representation(
            value=None
        )

        # Then
        assert api_representation_result is None

    def test_button_chooser_returns_expected_result(self):
        """
        Given `button_target_model`, mock data and a `ButtonChooserBlock()` instance
        When the `ButtonChooserBlock.get_api_representation()` is called with
            a `FakeSnippet()` instance
        Then `get_api_representation()` method will return the expected snippet instance fields
        """
        # Given
        button_target_model = "snippets.button"
        fake_snippet_data = {
            "text": "download",
            "loading_text": "downloading...",
            "endpoint": "/api/path",
            "method": "POST",
            "button_type": "DOWNLOAD",
        }
        snippet_instance = FakeButtonSnippet(**fake_snippet_data)
        button_chooser_block = ButtonChooserBlock(target_model=button_target_model)

        # When
        api_representation = button_chooser_block.get_api_representation(
            snippet_instance
        )
        # Then
        assert api_representation == fake_snippet_data
