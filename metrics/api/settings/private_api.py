import config
from metrics.api.settings.auth import AUTH_ENABLED

if AUTH_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config.REDIS_HOST,
            "KEY_PREFIX": "ukhsa",
        }
    }


DATABASES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": config.POSTGRES_DB,
        "USER": config.POSTGRES_USER,
        "PASSWORD": config.POSTGRES_PASSWORD,
        "HOST": config.POSTGRES_HOST,
        "PORT": config.POSTGRES_PORT,
        "POOL_OPTIONS": {
            "POOL_SIZE": 20,
            # Number of connections to be persisted at all times
            "MAX_OVERFLOW": 15,
            # Additional connections to be created at peak loads
            "RECYCLE": 8 * 60 * 60,
            # Time to close and replace connections
            "TIMEOUT": 60,
            # Period of time to wait for a connection to become available
            # during peak loads when all overflow slots are occupied
            "RESET_ON_RETURN": "rollback",
            # Reset on every connection return by rollback
        },
    }
}
