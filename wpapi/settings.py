import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': os.getenv('POSTGRES_HOST', ''),
                'port': '5432',
                'user': os.getenv('POSTGRES_USER', ''),
                'password': os.getenv('POSTGRES_PASSWORD', ''),
                'database': os.getenv('POSTGRES_DB', ''),
            }
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

TORTOISE_ORM_LOCAL = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'wp-db',
                'port': '5432',
                'user': 'postgres',
                'password': 'mysecretpassword',
                'database': 'postgres',
            }
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
