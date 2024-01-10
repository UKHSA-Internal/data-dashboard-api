from django.core.management.base import BaseCommand

from ingestion.operations.truncated_dataset import upload_truncated_test_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        multiprocessing_enabled: bool = options.get("multiprocessing_enabled", True)
        upload_truncated_test_data(multiprocessing_enabled=multiprocessing_enabled)

    def add_arguments(self, parser):
        parser.add_argument(
            "--multiprocessing_enabled",
            type=bool,
            required=False,
        )
