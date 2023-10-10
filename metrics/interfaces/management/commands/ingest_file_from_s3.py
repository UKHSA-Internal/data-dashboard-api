from django.core.management.base import BaseCommand

from ingestion.operations.upload_from_s3 import download_file_ingest_and_teardown


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file-key",
            type=str,
            help="The key of the file to ingest from the the s3 bucket.",
        )

    def handle(self, *args, **options) -> None:
        file_key = options.get("file_key")
        download_file_ingest_and_teardown(key=file_key)
