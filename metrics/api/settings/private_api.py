import os

import config

if os.environ.get("AUTH_ENABLED", False):
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
