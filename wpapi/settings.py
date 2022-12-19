import boto3
import json
import logging
import os

from botocore.exceptions import ClientError
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def get_secret():
    secret_name = "rds/postgres"
    region_name = "eu-west-2"
    service_name = 'secretsmanager'

    # Create a Secrets Manager client
    session = boto3.session.Session()
    logging.error("Session started")
    client = session.client(
        service_name=service_name,
        region_name=region_name
    )
    logging.error("Client started")

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        logging.error(str(e))
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secrets = json.loads(get_secret_value_response['SecretString'])
    logging.error(secrets)
    return secrets['rds_password']


def get_db_credentials():
    password = ''
    try:
        password = get_secret()
    except Exception as err:
        logging.error("Couldn't get the password from SecretManager")
        logging.error(err)
    else:
        logging.info("DB password set")

    return password


TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': os.getenv('POSTGRES_HOST', ''),
                'port': '5432',
                'user': 'wp_user',
                'password': '2397r943ht34erh'#os.getenv('POSTGRES_PASSWORD', '') or get_db_credentials(),
                'database': os.getenv('POSTGRES_DB', ''),
            }
        }
    },
    'apps': {
        'winter_pressures': {
            'models': ['wpapi.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'routers': None,
    'use_tz': False,
    'timezone': 'UTC'
}

TORTOISE_ORM_LOCAL = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'localhost',
                'port': '5432',
                'user': 'postgres',
                'password': 'mysecretpassword',
                'database': 'postgres',
            }
        }
    },
    'apps': {
        'winter_pressures': {
            'models': ['wpapi.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'routers': None,
    'use_tz': False,
    'timezone': 'UTC'
}
