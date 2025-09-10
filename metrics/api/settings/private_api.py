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
        },
        "reserved": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config.REDIS_RESERVED_HOST,
            "KEY_PREFIX": "reserved",
        },
    }
