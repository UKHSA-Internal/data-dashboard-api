import config

DATABASES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.POSTGRES_DB,
        "USER": config.POSTGRES_USER,
        "PASSWORD": config.POSTGRES_PASSWORD,
        "HOST": config.POSTGRES_HOST,
        "PORT": config.POSTGRES_PORT,
        "CONN_MAX_AGE": 60 * 60 * 1,
    }
}
