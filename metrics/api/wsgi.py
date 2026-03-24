"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metrics.api.settings")

application = get_wsgi_application()

# --------------------------------------------------------
# Telemetry init (runs once on startup)
# --------------------------------------------------------

from public_api.telemetry import telemetry
from config import APIENV, FRONTEND_URL

base_url = FRONTEND_URL or "http://localhost:8000"

telemetry.init(
    service="django-api",
    endpoint=f"{base_url}/api/telemetry/events",
    environment=APIENV or "dev",
)
