import pytest

from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_snippet,
    remove_buttons_snippets,
)
from cms.snippets.models.internal_button import Button, ButtonTypes, Methods


class TestButtonSnippetOperations:
    @pytest.mark.django_db
    def test_removes_all_buttons(self):
        """
        Given an existing `ButtonSnippet` model in the database
        When `remove_buttons_snippets()` is called
        Then all `ButtonSnippet` models are removed.
        """
        # Given
        Button.objects.create(
            text="mock button",
            loading_text="",
            endpoint="/api/mock_endpoint/v1",
            method=Methods.POST,
            button_type=ButtonTypes.DOWNLOAD,
        )
        assert Button.objects.exists()

        # When
        remove_buttons_snippets()

        # Then
        assert not Button.objects.exists()

    @pytest.mark.django_db
    def test_create_button_snippet(self):
        """
        Given No existing `ButtonSnippet` snippets in the database
        When the `create_download_button_snippet()` operation is called
        Then a new `ButtonSnippet` item entry will be created.
        """
        # Given
        remove_buttons_snippets()
        assert not Button.objects.exists()

        # When
        button_snippet = get_or_create_download_button_snippet()

        # Then
        assert button_snippet.text == "download (zip)"
        assert button_snippet.loading_text == ""
        assert button_snippet.endpoint == "/api/bulkdownloads/v1"
        assert button_snippet.method == "POST"
        assert button_snippet.button_type == "DOWNLOAD"
