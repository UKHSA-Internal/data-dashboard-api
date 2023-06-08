from django.core.management.base import BaseCommand

from metrics.data.operations.core_models import load_core_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_core_data(filename="test_data.csv")
