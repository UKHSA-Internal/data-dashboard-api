import logging
import os

import django.core.management.utils
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

# The environment in which this app is running in.
# If this is set to "LOCAL" or "STANDALONE" then a local sqlite db will be used
# If this is set to any value other than "LOCAL" or "STANDALONE"
#   then the `POSTGRES` credentials below
#   will be used to connect to a remote database
APIENV = os.environ.get("APIENV")

# Database configuration
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Workload type switch. This setting controls which endpoints to expose
# If it is not set, then the complete set of endpoints will be used.
APP_MODE = os.environ.get("APP_MODE")

# Django `SECRET_KEY` used to provide cryptographic signing of values
SECRET_KEY = os.environ.get("SECRET_KEY")
# If not provided then generate a new one.
# Note that this will mean sessions and cookies will be lost between deployments,
# if the `SECRET_KEY` is then set to another value.
if not SECRET_KEY:
    logger.info("No `SECRET_KEY` provided, generating random secret key instead.")
    SECRET_KEY = django.core.management.utils.get_random_secret_key()

# URL for the frontend application.
# Note this is only used for a link on the public API
# to direct users back to the frontend dashboard
FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

# Email server configuration
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", True)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

# The recipient address to send feedback emails to
FEEDBACK_EMAIL_RECIPIENT_ADDRESS = os.environ.get("FEEDBACK_EMAIL_RECIPIENT_ADDRESS")

# The endpoint of the Redis cache
REDIS_HOST = os.environ.get("REDIS_HOST", "")
if not REDIS_HOST:
    logger.info("No REDIS_HOST given, falling back to localhost")
    REDIS_HOST = "redis://127.0.0.1:6379"

# The name of the s3 bucket used for ingestion
INGESTION_BUCKET_NAME = os.environ.get("INGESTION_BUCKET_NAME")
# The name of the AWS profile to use for the AWS client used for ingestion
AWS_PROFILE_NAME = os.environ.get("AWS_PROFILE_NAME")
