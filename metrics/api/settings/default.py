"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "metrics.data",
    "metrics.interfaces",
]

if config.APP_MODE != "INGESTION":
    INSTALLED_APPS += [
        "django_filters",
        "corsheaders",
        "rest_framework",
        "drf_spectacular",
        "metrics.api",
        "cms.home",
        "cms.topic",
        "cms.dashboard",
        "cms.common",
        "cms.composite",
        "cms.whats_new",
        "cms.metrics_documentation",
        "cms.snippets",
        "cms.forms",
        "wagtail.api.v2",
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail_modeladmin",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail",
        "wagtail_trash",
        "modelcluster",
        "taggit",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

APPEND_SLASH = True

ROOT_URLCONF = "metrics.api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "metrics.api.context_processors.frontend_url",
            ],
        },
    },
]


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    "PREPROCESSING_HOOKS": ["metrics.api.open_api.pre_processing_endpoint_filter_hook"],
    "TITLE": "UKHSA Data Dashboard API Docs",
    "DESCRIPTION": "Docs for the API which supports the UKHSA Data Dashboard.",
    "VERSION": "v 0.1.0",
}

WSGI_APPLICATION = "metrics.api.wsgi.application"

# Caching configuration
CACHE_TTL = None
# This means that the cache will only be refreshed explicitly

# Use the in-memory cache backend provided by Django
# when the application is not running in private API mode
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# Puts the db at the root level of the repo instead of within the `metrics` app
ROOT_LEVEL_BASE_DIR = BASE_DIR.parent

DATABASES = {
    "default": {
        "TIME_ZONE": "Europe/London",
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": config.POSTGRES_DB,
        "USER": config.POSTGRES_USER,
        "PASSWORD": config.POSTGRES_PASSWORD,
        "HOST": config.POSTGRES_HOST,
        "PORT": config.POSTGRES_PORT,
        "POOL_OPTIONS": {
            "POOL_SIZE": 10,
            # Number of connections to be persisted at all times
            "MAX_OVERFLOW": 10,
            # Additional connections to be created at peak loads
            "RECYCLE": 24 * 60 * 60,
            # Time to close and replace connections
            "TIMEOUT": 60 * 10,
            # Period of time to wait for a connection to become available
            # during peak loads when all overflow slots are occupied
        },
    }
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": f"%(asctime)s [%(levelname)s] [ENVIRONMENT:{config.APIENV}] [%(name)s - %(funcName)s] %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": config.LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {  # Default logger
            "handlers": ["console"],
            "level": config.LOG_LEVEL,
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": config.LOG_LEVEL,
            "propagate": False,
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/London"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]


# Wagtail settings

WAGTAIL_SITE_NAME = "dashboard"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = "http://example.com"

# Controls the maximum number of results which can be requested from the pages API.
# Set to None for no limit.
WAGTAILAPI_LIMIT_MAX = None


CSRF_TRUSTED_ORIGINS = ["https://*.ukhsa-dashboard.data.gov.uk"]
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
