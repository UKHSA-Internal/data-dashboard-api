import config

# Only use the configured Redis cache when the application is running in private API mode
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config.REDIS_HOST,
        "KEY_PREFIX": "ukhsa",
    }
}
