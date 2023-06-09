from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.upload_test_data"


class TestUploadTestData:
    @mock.patch(f"{MODULE_PATH}.load_core_data")
    def test_delegates_call(self, spy_load_core_data: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `upload_test_data`
        Then the call is delegated to the `load_core_data()` function
        """
        # Given / When
        call_command("upload_test_data")

        # Then
        spy_load_core_data.assert_called_once_with(filename="test_data.csv")
