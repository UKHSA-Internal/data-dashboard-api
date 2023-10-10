from unittest import mock

from django.core.management import call_command

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
