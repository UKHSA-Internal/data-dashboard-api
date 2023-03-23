from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        try:
            from metrics.data.operations.core_models import load_core_data

            # load_core_data("source_data/daily_data_alpha_17032023.csv")
            # load_core_data("tests/fixtures/sample_data.csv")
            load_core_data("source_data/data_alpha_22032023.csv")

            # from metrics.data.operations.api_models import generate_api_time_series

            # generate_api_time_series()

        except Exception as e:
            self.stderr.write(f"Uh oh, Data Loader failed: {str(e)}")
        else:
            self.stdout.write("Data Loaded successfully")
