import os

from metrics.api.settings import (
    INSTALLED_APPS,
    MIDDLEWARE,
    ROOT_LEVEL_BASE_DIR,
)

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

DEBUG = True

DATABASES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_LEVEL_BASE_DIR, "db.sqlite3"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "reserved": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "KEY_PREFIX": "reserved",
    },
}

# Debug toolbar configuration
INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Silk profiling configuration
SILK_PROFILING_ENABLED = os.environ.get("SILK_PROFILING_ENABLED", "false").lower() in {
    "true",
    "1",
}

if SILK_PROFILING_ENABLED:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += [
        "silk.middleware.SilkyMiddleware",
        "metrics.api.middleware.silky.SilkProfileAllViewsMiddleware",
    ]
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True


INTERNAL_IPS = ["127.0.0.1"]

PAGE_PREVIEWS_ENABLED = os.environ.get("PAGE_PREVIEWS_ENABLED", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
