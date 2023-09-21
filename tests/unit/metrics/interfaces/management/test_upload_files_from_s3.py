from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.upload_files_from_s3"


class TestUploadFilesFromS3:
    @mock.patch(f"{MODULE_PATH}.download_files_and_upload")
    def test_delegates_call(self, spy_download_files_and_upload: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `upload_files_from_s3`
        Then the call is delegated to the `download_files_and_upload()` function
        """
        # Given / When
        call_command("upload_files_from_s3")

        # Then
        spy_download_files_and_upload.assert_called_once()
