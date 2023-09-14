from django.core.management.base import BaseCommand

from metrics.data.operations.truncated_dataset import upload_truncated_test_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        upload_truncated_test_data()
