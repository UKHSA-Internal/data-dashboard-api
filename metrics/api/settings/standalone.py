import os

from metrics.api.settings import ROOT_LEVEL_BASE_DIR

DATABASES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_LEVEL_BASE_DIR, "db.sqlite3"),
    }
}
