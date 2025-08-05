from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.upload_truncated_test_data"


class TestUploadTruncatedTestDataCommand:
    @mock.patch(f"{MODULE_PATH}.upload_truncated_test_data")
    def test_delegates_call(self, spy_upload_truncated_test_data: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `upload_truncated_test_data`
        Then the call is delegated to the `upload_truncated_test_data()` function
        """
        # Given / When
        call_command("upload_truncated_test_data")

        # Then
        spy_upload_truncated_test_data.assert_called_once()
