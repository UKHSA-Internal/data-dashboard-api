import json
import os

import boto3


class MissingSecretsManagerARNError(Exception):
    def __init__(self):
        message = "The `SECRETS_MANAGER_DB_CREDENTIALS_ARN` environment variable should be provided"
        super().__init__(message)


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

    secrets_manager_client = boto3.client("secretsmanager")
    returned_secret: str = secrets_manager_client.get_secret_value(
        SecretId=db_credentials_secret_arn
    )
    loaded_secret: dict[str, str] = json.loads(returned_secret)
    return loaded_secret["SecretString"]["password"]
