from unittest import mock

from django.core.management import call_command

from metrics.data.models.api_keys import CustomAPIKey

MODULE_PATH = "metrics.interfaces.management.commands.create_api_key"


class TestCreateAPIKey:
    @mock.patch(f"{MODULE_PATH}.uuid")
    @mock.patch.object(CustomAPIKey, "objects")
    def test_calling_command_without_passwords_can_be_done_successfully(
        self,
        spy_api_key_model_manager: mock.MagicMock,
        mocked_uuid: mock.MagicMock,
    ):
        """
        Given no `password_prefix` or `password_suffix`
        When a call is made to the custom management command `create_api_key`
        Then the call is delegated to the `create_key()` method on the model manager
        """
        # Given / When
        call_command("create_api_key")

        # Then
        expected_unique_id = str(mocked_uuid.uuid4.return_value)
        spy_api_key_model_manager.create_key.assert_called_once_with(
            name=expected_unique_id
        )

    @mock.patch(f"{MODULE_PATH}.uuid")
    @mock.patch.object(CustomAPIKey, "objects")
    def test_calling_command_with_password_will_pass_them_to_model_manager(
        self,
        spy_api_key_model_manager: mock.MagicMock,
        mocked_uuid: mock.MagicMock,
    ):
        """
        Given a `password_prefix` and a `password_suffix`
        When a call is made to the custom management command `create_api_key`
        Then the call is delegated to the `create_key()` method on the model manager
        And the password components are passed through
        """
        # Given
        password_prefix = "123456788"
        password_suffix = "123456789123456789123456789"

        # When
        call_command(
            "create_api_key",
            password_prefix=password_prefix,
            password_suffix=password_suffix,
        )

        # Then
        expected_unique_id = str(mocked_uuid.uuid4.return_value)
        spy_api_key_model_manager.create_key.assert_called_once_with(
            name=expected_unique_id,
            password_prefix=password_prefix,
            password_suffix=password_suffix,
        )

    @mock.patch(f"{MODULE_PATH}.uuid")
    @mock.patch.object(CustomAPIKey, "objects")
    def test_calling_command_with_password_prefix_only_will_pass_to_model_manager(
        self,
        spy_api_key_model_manager: mock.MagicMock,
        mocked_uuid: mock.MagicMock,
    ):
        """
        Given a `password_prefix` but no `password_suffix`
        When a call is made to the custom management command `create_api_key`
        Then the call is delegated to the `create_key()` method on the model manager
        And the available password component is passed through
        """
        # Given
        password_prefix = "123456788"

        # When
        call_command("create_api_key", password_prefix=password_prefix)

        # Then
        expected_unique_id = str(mocked_uuid.uuid4.return_value)
        spy_api_key_model_manager.create_key.assert_called_once_with(
            name=expected_unique_id,
            password_prefix=password_prefix,
        )

    @mock.patch(f"{MODULE_PATH}.uuid")
    @mock.patch.object(CustomAPIKey, "objects")
    def test_calling_command_with_password_suffix_only_will_pass_to_model_manager(
        self,
        spy_api_key_model_manager: mock.MagicMock,
        mocked_uuid: mock.MagicMock,
    ):
        """
        Given a `password_suffix` but no `password_prefix`
        When a call is made to the custom management command `create_api_key`
        Then the call is delegated to the `create_key()` method on the model manager
        And the available password component is passed through
        """
        # Given
        password_suffix = "123456789123456789123456789"

        # When
        call_command("create_api_key", password_suffix=password_suffix)

        # Then
        expected_unique_id = str(mocked_uuid.uuid4.return_value)
        spy_api_key_model_manager.create_key.assert_called_once_with(
            name=expected_unique_id,
            password_suffix=password_suffix,
        )
