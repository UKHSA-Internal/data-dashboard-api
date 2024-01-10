import json
from unittest import mock

import pytest

from ingestion.secrets_manager import (
    MissingSecretsManagerARNError,
    get_database_password,
)

MODULE_PATH = "ingestion.secrets_manager"


def build_fake_returned_secret_from_secrets_manager(
    password: str = "",
) -> dict[str, str]:
    serialized_secret: str = json.dumps(
        obj={
            "username": "fake-user-name",
            "password": password,
        }
    )
    return {"SecretString": serialized_secret}


class TestGetDatabasePassword:
    @mock.patch(f"{MODULE_PATH}.boto3.client")
    def test_can_extract_password_from_returned_secret(
        self, spy_boto3_client: mock.MagicMock, monkeypatch
    ):
        """
        Given a value provided for the `SECRETS_MANAGER_DB_CREDENTIALS_ARN`
            environment variable
        When `get_database_password()` is called
        Then `get_secret_value()`

        Patches:
            `spy_boto3_client`: To remove the side effect
                of having to make a call to AWS
        """
        # Given
        fake_password = "abc"  # noqa: S105
        monkeypatch.setenv("SECRETS_MANAGER_DB_CREDENTIALS_ARN", "fake-arn")
        spy_boto3_client.return_value.get_secret_value.return_value = (
            build_fake_returned_secret_from_secrets_manager(password=fake_password)
        )

        # When
        returned_password: str = get_database_password()

        # Then
        assert returned_password == fake_password

    @mock.patch(f"{MODULE_PATH}.boto3.client")
    def test_uses_correct_env_var_for_secret_id_when_fetching_secret(
        self, spy_boto3_client: mock.MagicMock, monkeypatch
    ):
        """
        Given a value provided for the `SECRETS_MANAGER_DB_CREDENTIALS_ARN`
            environment variable
        When `get_database_password()` is called
        Then `get_secret_value()`

        Patches:
            `spy_boto3_client`: To remove the side effect
                of having to make a call to AWS
        """
        # Given
        fake_db_credentials_arn = "fake-arn"
        monkeypatch.setenv(
            "SECRETS_MANAGER_DB_CREDENTIALS_ARN", fake_db_credentials_arn
        )
        spy_secrets_manager_client = spy_boto3_client.return_value
        # This is mocked to avoid the side effect of having
        # to deserialize a JSON string which would
        # otherwise come back as a mock object
        spy_secrets_manager_client.get_secret_value.return_value = (
            build_fake_returned_secret_from_secrets_manager()
        )

        # When
        get_database_password()

        # Then
        spy_secrets_manager_client.get_secret_value.assert_called_once_with(
            SecretId=fake_db_credentials_arn
        )

    def test_raises_error_when_env_var_not_provided(self, monkeypatch):
        """
        Given the `SECRETS_MANAGER_DB_CREDENTIALS_ARN`
            environment variable has not been set
        When `get_database_password()` is called
        Then a `MissingSecretsManagerARNError` is raised
        """
        # Given
        monkeypatch.delenv("SECRETS_MANAGER_DB_CREDENTIALS_ARN", raising=False)

        # When / Then
        with pytest.raises(MissingSecretsManagerARNError):
            get_database_password()
