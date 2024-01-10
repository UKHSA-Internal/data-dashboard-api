import datetime
import json
import os

import boto3

SECRETS_MANAGER_RESPONSE_TYPE = dict[str, str | list[str] | datetime.datetime]


class MissingSecretsManagerARNError(Exception):
    def __init__(self):
        message = "The `SECRETS_MANAGER_DB_CREDENTIALS_ARN` environment variable should be provided"
        super().__init__(message)


def _extract_password_from_secret(secret: SECRETS_MANAGER_RESPONSE_TYPE) -> str:
    deserialized_secret: str = json.loads(secret["SecretString"])
    return deserialized_secret["password"]


def _request_secret_from_secrets_manager(
    db_credentials_secret_arn: str,
) -> SECRETS_MANAGER_RESPONSE_TYPE:
    secrets_manager_client = boto3.client("secretsmanager")
    return secrets_manager_client.get_secret_value(SecretId=db_credentials_secret_arn)


def get_database_password() -> str:
    """Fetches the database password from AWS secrets manager

    Notes:
        This function makes a call to external AWS services (SecretsManager).
        And therefore will incur both a performance and cost penalty.

    Returns:
        The database password as a raw string

    Raises:
        `MissingSecretsManagerARNError`: If the
            "SECRETS_MANAGER_DB_CREDENTIALS_ARN"
            environment variable has not been set

    """
    try:
        db_credentials_secret_arn: str = os.environ[
            "SECRETS_MANAGER_DB_CREDENTIALS_ARN"
        ]
    except KeyError as error:
        raise MissingSecretsManagerARNError from error

    secret: SECRETS_MANAGER_RESPONSE_TYPE = _request_secret_from_secrets_manager(
        db_credentials_secret_arn=db_credentials_secret_arn
    )
    return _extract_password_from_secret(secret=secret)
