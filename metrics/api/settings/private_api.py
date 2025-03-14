import os

import config


def is_auth_enabled():
    return os.environ.get("AUTH_ENABLED", "").lower() in {"true", "1"}


AUTH_ENABLED = is_auth_enabled()


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
