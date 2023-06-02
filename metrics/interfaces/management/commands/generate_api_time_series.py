from django.core.management.base import BaseCommand

from metrics.data.operations.api_models import generate_api_time_series


class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_api_time_series()
