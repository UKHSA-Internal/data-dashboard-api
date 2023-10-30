from unittest import mock

import pytest
from django.core.management import call_command

from metrics.interfaces.management.commands.ingest_file_from_s3 import (
    NoFileKeyProvidedToIngestError,
    _get_file_key_from_options_or_env_var,
)

MODULE_PATH = "metrics.interfaces.management.commands.ingest_file_from_s3"


class TestUploadFilesFromS3:
    @mock.patch(f"{MODULE_PATH}.download_file_ingest_and_teardown")
    def test_delegates_call(
        self, spy_download_file_ingest_and_teardown: mock.MagicMock
    ):
        """
        Given an instance of the app
        When a call is made to the
            custom management command `ingest_file_from_s3`
        Then the call is delegated to the
            `download_file_ingest_and_teardown()` function
        """
        # Given
        file_key = "abc.json"

        # When
        call_command("ingest_file_from_s3", file_key=file_key)

        # Then
        spy_download_file_ingest_and_teardown.assert_called_once_with(key=file_key)

    @mock.patch(f"{MODULE_PATH}._get_file_key_from_options_or_env_var")
    @mock.patch(f"{MODULE_PATH}.download_file_ingest_and_teardown")
    def test_delegates_call_to_determine_file_key(
        self,
        spy_download_file_ingest_and_teardown: mock.MagicMock,
        spy_get_file_key_from_options_or_env_var: mock.MagicMock,
    ):
        """
        Given an instance of the app
        When a call is made to the
            custom management command `ingest_file_from_s3`
        Then the call is delegated to the
            `download_file_ingest_and_teardown()` function

        Patches:
            `spy_download_file_ingest_and_teardown`: For the
                main assertion of checking the correct file key is used
            `spy_get_file_key_from_options_or_env_var`: To isolate
                the correct file key being determined from the
                call to `_get_file_key_from_options_or_env_var()`
        """
        # Given
        file_key = "abc.json"

        # When
        call_command("ingest_file_from_s3", file_key=file_key)

        # Then
        expected_file_key = spy_get_file_key_from_options_or_env_var.return_value
        spy_download_file_ingest_and_teardown.assert_called_once_with(
            key=expected_file_key
        )


class TestGetFileKeyFromOptionsOrEnvVar:
    def test_returns_file_key_from_input_options_if_available(self):
        """
        Given a dict which contains a "file_key"
        When `_get_file_key_from_options_or_env_var()` is called
        Then the correct file key is returned
        """
        # Given
        fake_file_key = "abc"
        options = {"file_key": fake_file_key}

        # When
        file_key: str = _get_file_key_from_options_or_env_var(options=options)

        # Then
        assert file_key == fake_file_key

    def test_returns_file_key_from_env_var_as_fallback(self, monkeypatch):
        """
        Given a dict which does not contain a "file_key"
        And an `S3_OBJECT_KEY` environment variable
        When `_get_file_key_from_options_or_env_var()` is called
        Then the correct file key is returned
        """
        # Given
        fake_file_key = "abc"
        monkeypatch.setenv("S3_OBJECT_KEY", fake_file_key)
        options = {}

        # When
        file_key: str = _get_file_key_from_options_or_env_var(options=options)

        # Then
        assert file_key == fake_file_key

    def test_raises_error_when_no_file_key_available_and_empty_string_set_as_env_var(
        self, monkeypatch
    ):
        """
        Given a dict which does not contain a "file_key"
        And an empty string has been set for the `S3_OBJECT_KEY` environment variable
        When `_get_file_key_from_options_or_env_var()` is called
        Then a `NoFileKeyProvidedToIngestError` is raised
        """
        # Given
        monkeypatch.setenv("S3_OBJECT_KEY", "")
        options = {}

        # When / Then
        with pytest.raises(NoFileKeyProvidedToIngestError):
            _get_file_key_from_options_or_env_var(options=options)

    def test_raises_error_when_no_file_key_available_and_no_env_var_set(
        self, monkeypatch
    ):
        """
        Given a dict which does not contain a "file_key"
        And no value for the `S3_OBJECT_KEY` environment variable
        When `_get_file_key_from_options_or_env_var()` is called
        Then a `NoFileKeyProvidedToIngestError` is raised
        """
        # Given
        monkeypatch.delenv("S3_OBJECT_KEY", raising=False)
        options = {}

        # When / Then
        with pytest.raises(NoFileKeyProvidedToIngestError):
            _get_file_key_from_options_or_env_var(options=options)
