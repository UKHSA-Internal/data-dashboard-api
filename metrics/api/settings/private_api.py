import os

import config

AUTH_ENABLED: bool = os.environ.get("AUTH_ENABLED", "").lower() in {"true", "1"}

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
