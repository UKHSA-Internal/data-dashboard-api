from cms.dynamic_content.blocks import WhaButtonChooserBlock
from tests.fakes.models.cms.what_button_snippet import FakeWhaButtonSnippet


class TestWhaButtonChooser:
    def test_wha_button_chooser_return_none(self):
        """
        Given an wha_button_target_model and a `WhaButtonChooserBlock()` instance
        When the `WhaButtonChooserBlock.get_api_representation()` is called with
            None instead of a snippet instance
        Then None is returned.
        """
        # Given
        wha_button_target_model = "snippets.whabutton"
        wha_button_chooser_block = WhaButtonChooserBlock(
            target_model=wha_button_target_model
        )

        # Then
        api_representation_result = wha_button_chooser_block.get_api_representation(
            value=None
        )

        # Then
        assert api_representation_result is None

    def test_wha_button_chooser_returns_expected_result(self):
        """
        Given `wha_button_target_model`, fake data and a `WhaButtonChooserBlock()` instance
        When the `WhaButtonChooserBlock.get_api_representation()` is called with
            a `FakeSnippet()` instance
        Then `get_api_representation()` method will return the expected snippet instance fields
        """
        # Given
        wha_button_target_model = "snippets.whabutton"
        fake_snippet_data = {
            "text": "view map",
            "button_type": "Heat",
            "geography_code": "E12000001",
        }
        snippet_instance = FakeWhaButtonSnippet(**fake_snippet_data)
        wha_button_chooser_block = WhaButtonChooserBlock(
            target_model=wha_button_target_model
        )

        # When
        api_representation = wha_button_chooser_block.get_api_representation(
            snippet_instance
        )

        # Then
        assert api_representation == fake_snippet_data
