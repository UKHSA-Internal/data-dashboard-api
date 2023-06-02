from unittest import mock

from django.core.management import call_command

from metrics.data.models.api_keys import CustomAPIKey

MODULE_PATH = "metrics.interfaces.management.commands.create_api_key"


class TestCreateAPIKey:
    @mock.patch.object(CustomAPIKey, "objects")
    def test_delegates_call(self, spy_api_key_model_manager: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `create_api_key`
        Then the call is delegated to the `create_key()` method on the model manager
        """
        # Given
        spy_api_key_model_manager.create_key.return_value = mock.Mock(), mock.Mock()

        # When
        call_command("create_api_key")

        # Then
        spy_api_key_model_manager.create_key.assert_called_once()
