import logging
import os
from os.path import dirname, join

import django.core.management.utils
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

# The environment in which this app is running in.
# If this is set to "LOCAL" then a local sqlite db will be used
# If this is set to any value other than "LOCAL"
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
