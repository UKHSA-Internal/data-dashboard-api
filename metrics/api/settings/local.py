import os

from metrics.api.settings import INSTALLED_APPS, MIDDLEWARE, ROOT_LEVEL_BASE_DIR

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

INTERNAL_IPS = ["127.0.0.1"]
