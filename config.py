import os
from os.path import dirname, join

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

APIENV = os.environ.get("APIENV")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)

FRONTEND_API_URL = os.environ.get("FRONTEND_API_URL", "")
FRONTEND_API_KEY = os.environ.get("FRONTEND_API_KEY", "")


class EnvVarNotSetError(Exception):
    ...


if APIENV not in ("DEV", "PROD"):
    raise EnvVarNotSetError("APIENV environment variable should be set to DEV or PROD")
