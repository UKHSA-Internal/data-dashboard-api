import pytest

from cms.snippets.data_migrations.operations import (
    create_download_button_snippet,
    remove_buttons_snippets,
)
from cms.snippets.models import Button, ButtonTypes, Methods


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
        create_download_button_snippet()

        # Then
        assert Button.objects.exists()
