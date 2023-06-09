import os
from os.path import dirname, join

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

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
