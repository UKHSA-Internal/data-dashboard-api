import logging
import os

from django.core.management.base import BaseCommand

from ingestion.operations.upload_from_s3 import download_file_ingest_and_teardown

logger = logging.getLogger(__name__)


class NoFileKeyProvidedToIngestError(Exception):
    def __init__(self):
        message = "No file key provided to the ingestion process"
        super().__init__(message)


def _get_file_key_from_options_or_env_var(options: dict) -> str:
    """Extracts the file key from the given `options` dict, otherwise tries the "S3_OBJECT_KEY" env var

    Args:
        options: The dict passed to the management command

    Returns:
        String representing the full file key
        E.g. "in/COVID-19_cases_casesByDay.json"

    Raises:
        `NoFileKeyProvidedToIngestError`: If a file key
            could not be found from the input `options` dict
            or from the "S3_OBJECT_KEY" environment variable

    """
    file_key: str | None = options.get("file_key") or os.environ.get("S3_OBJECT_KEY")

    if not file_key:
        raise NoFileKeyProvidedToIngestError

    return file_key


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file-key",
            type=str,
            help="The key of the file to ingest from the the s3 bucket.",
        )

    def handle(self, *args, **options) -> None:
        file_key: str = _get_file_key_from_options_or_env_var(options=options)
        download_file_ingest_and_teardown(key=file_key)
