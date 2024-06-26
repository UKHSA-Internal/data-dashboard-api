from cms.dynamic_content.blocks import ExternalButtonChooserBlock
from tests.fakes.models.cms.external_button_snippet import FakeExternalButtonSnippet


class TestExternalButtonChooser:
    def test_button_chooser_return_none(self):
        """
        Given a external_button_target_model  and a `ExternalButtonChooserBlock()` instance
        When the `ExternalButtonChooserBlock.get_api_representation()` is called with
            None instead of a snippet instance
        Then None is returned.
        """
        # Given
        external_button_target_model = "snippets.externalbutton"
        external_button_chooser_block = ExternalButtonChooserBlock(
            target_model=external_button_target_model
        )

        # Then
        api_representation_result = (
            external_button_chooser_block.get_api_representation(value=None)
        )

        # Then
        assert api_representation_result is None

    def test_button_chooser_returns_expected_result(self):
        """
        Given `external_button_target_model`, mock data and a `ExternalButtonChooserBlock()` instance
        When the `ExternalButtonChooserBlock.get_api_representation()` is called with
            a `FakeSnippet()` instance
        Then `get_api_representation()` method will return the expected snippet instance fields
        """
        # Given
        external_button_target_model = "snippets.externalbutton"
        fake_snippet_data = {
            "text": "download",
            "url": "https://www.google.com",
            "button_type": "Primary",
            "icon": "Download",
        }
        snippet_instance = FakeExternalButtonSnippet(**fake_snippet_data)
        external_button_chooser_block = ExternalButtonChooserBlock(
            target_model=external_button_target_model
        )

        # When
        api_representation = external_button_chooser_block.get_api_representation(
            snippet_instance
        )
        # Then
        assert api_representation == fake_snippet_data
