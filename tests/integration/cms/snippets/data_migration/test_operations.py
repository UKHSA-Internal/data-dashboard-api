import pytest

from _pytest.logging import LogCaptureFixture

from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_internal_button_snippet,
    get_or_create_download_button_snippet,
    remove_buttons_snippets,
    remove_internal_button_snippets,
)
from cms.snippets.models.internal_button import InternalButton, InternalButtonTypes


class TestButtonSnippetOperations:
    def test_remove_all_buttons_function_logs_message(
        self,
        caplog: LogCaptureFixture,
    ):
        """
        Given an expected log message
        When the deprecated migration operation `remove_buttons_snippets()` is called
        Then the expected log is returned
        """
        # Given
        expected_log = (
            "Button snippet has been removed and replaced by InternalButton snippet."
        )

        # When
        remove_buttons_snippets()

        # Then
        assert expected_log in caplog.text

    def test_get_or_remove_download_button(
        self,
        caplog: LogCaptureFixture,
    ):
        """
        Given an expected log message
        When the deprecated migration operation `get_or_create_download_button_snippet()` is called
        Then the expected log is returned
        """
        # Given
        expected_log = (
            "Button snippet has been removed and replaced by InternalButton snippet."
        )

        # When
        get_or_create_download_button_snippet()

        # Then
        assert expected_log in caplog.text


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
