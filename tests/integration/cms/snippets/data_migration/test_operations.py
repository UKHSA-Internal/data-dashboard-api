import pytest

from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_internal_button_snippet,
    get_or_create_download_button_snippet,
    remove_buttons_snippets,
    remove_internal_button_snippets,
)
from cms.snippets.models.button import Button, ButtonTypes, Methods
from cms.snippets.models.internal_button import InternalButton, InternalButtonTypes


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


class TestInternalButtonSnippetOperations:

    @pytest.mark.django_db
    def test_removes_all_internal_buttons(self):
        """
        Given an existing `InternalButtonSnippet` model in the database
        When `remove_internal_buttons_snippets()` is called
        Then all `InternalButtonSnippet` models are removed.
        """
        # Given
        InternalButton.objects.create(
            text="mock button",
            button_type=InternalButtonTypes.BULK_DOWNLOAD.value,
        )
        assert InternalButton.objects.exists()

        # When
        remove_internal_button_snippets()

        # Then
        assert not InternalButton.objects.exists()

    @pytest.mark.django_db
    def test_create_internal_button_snippet(self):
        """
        Given no existing `InternalButtonSnippet` snippets in the database
        When the `create_download_internal_button_snippet()` operation is called
        Then a new `InternalButtonSnippet` item entry will be created.
        """
        # Given
        """
        There is a data migration for an initial `InternalButton` snippet,
        which needs removing at the start of the test.
        """
        remove_internal_button_snippets()
        assert not InternalButton.objects.exists()

        # When
        internal_button_snippet = (
            get_or_create_download_button_internal_button_snippet()
        )

        # Then
        assert internal_button_snippet.text == "download (zip)"
        assert internal_button_snippet.button_type == "BULK_DOWNLOAD"
        assert internal_button_snippet.endpoint == "/api/bulkdownloads/v1"
        assert internal_button_snippet.method == "POST"
