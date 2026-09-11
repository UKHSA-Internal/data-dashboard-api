import os

from metrics.api.settings import ROOT_LEVEL_BASE_DIR

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

DEBUG = True

DATABASES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_LEVEL_BASE_DIR, "test.sqlite3"),
    },
    "test": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_LEVEL_BASE_DIR, "test.sqlite3"),
    },
}

INTERNAL_IPS = ["127.0.0.1"]
