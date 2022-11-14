import os

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'localhost',
                'port': '5432',
                'user': 'postgres',
                'password': 'mysecretpassword',  # Obviously wrong, for testing
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
