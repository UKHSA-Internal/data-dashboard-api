from django.core.management.base import BaseCommand

from ingestion.operations.upload_from_s3 import download_files_and_upload


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        download_files_and_upload()
