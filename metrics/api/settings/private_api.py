import config

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
