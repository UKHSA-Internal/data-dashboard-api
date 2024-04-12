from cms.dynamic_content.blocks import InternalButtonChooserBlock
from tests.fakes.models.cms.internal_button_snippet import FakeInternalButtonSnippet


class TestInternalButtonChooser:
    def test_internal_button_chooser_return_none(self):
        """
        Given an internal_button_target_model  and a `InternalButtonChooserBlock()` instance
        When the `ExternalButtonChooserBlock.get_api_representation()` is called with
            None instead of a snippet instance
        Then None is returned.
        """
        # Given
        internal_button_target_model = "snippets.internalbutton"
        internal_button_chooser_block = InternalButtonChooserBlock(
            target_model=internal_button_target_model
        )

        # Then
        api_representation_result = (
            internal_button_chooser_block.get_api_representation(value=None)
        )

        # Then
        assert api_representation_result is None

    def test_internal_button_chooser_returns_expected_result(self):
        """
        Given `internal_button_target_model`, mock data and a `InternalButtonChooserBlock()` instance
        When the `InternalButtonChooserBlock.get_api_representation()` is called with
            a `FakeSnippet()` instance
        Then `get_api_representation()` method will return the expected snippet instance fields
        """
        # Given
        internal_button_target_model = "snippets.internalbutton"
        fake_snippet_data = {
            "text": "download",
            "button_type": "BULK_DOWNLOAD",
            "endpoint": "/api/bulkdownloads/v1/",
            "method": "POST",
        }
        snippet_instance = FakeInternalButtonSnippet(**fake_snippet_data)
        internal_button_chooser_block = InternalButtonChooserBlock(
            target_model=internal_button_target_model
        )

        # When
        api_representation = internal_button_chooser_block.get_api_representation(
            snippet_instance
        )
        # Then
        assert api_representation == fake_snippet_data
