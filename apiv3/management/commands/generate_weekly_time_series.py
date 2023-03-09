from django.core.management.base import BaseCommand

from apiv3.api_models import generate_weekly_time_series


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        try:
            generate_weekly_time_series()
        except Exception:
            self.stderr.write("Uh oh, something bad happened")
        else:
            self.stdout.write("Generated weekly time series")
