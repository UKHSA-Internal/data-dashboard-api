from metrics.api.settings.auth import AUTH_ENABLED

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    "PREPROCESSING_HOOKS": ["metrics.api.open_api.pre_processing_endpoint_filter_hook"],
    "TITLE": "UKHSA Data Dashboard API Docs",
    "DESCRIPTION": "Docs for the API which supports the UKHSA Data Dashboard. ",
    "VERSION": "v 0.1.0",
}

if AUTH_ENABLED:
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "public_api.middleware.NoIndexNoFollowMiddleware",  # Add noindex, nofollow robots-tag middleware for non-public
    ]
