import boto3
import json
import os

from botocore.exceptions import ClientError
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

APIENV = os.getenv('APIENV', 'PROD').upper()


def get_secret():
    secret_name = "rds/postgres"
    region_name = "eu-west-2"
    service_name='secretsmanager'

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name=service_name,
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secrets = json.loads(get_secret_value_response['SecretString'])

    return secrets['rds_password']


# It's a function (not a constant as before) so the prod related stuff
# won't be executed, for example get_secret()
def get_db_credentials():
    if APIENV == 'DEV':
        return {
            'host': 'wp-net',
            'port': '5432',
            'user': 'postgres',
            'password': 'mysecretpassword',
            'database': 'postgres',
        }

    return {
        'host': os.getenv('POSTGRES_HOST', ''),
        'port': '5432',
        'user': os.getenv('POSTGRES_USER', ''),
        'password': (
            os.getenv('POSTGRES_PASSWORD', '') if APIENV == 'DEV' else get_secret()
        ),
        'database': os.getenv('POSTGRES_DB', ''),
    }


TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': get_db_credentials()
        }
    },
    'apps': {
        'winter_pressures': {
            'models': ['models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'UTC'
}
