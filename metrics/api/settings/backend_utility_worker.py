import config

CACHES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config.REDIS_HOST,
        "KEY_PREFIX": "ukhsa",
    }
}
