from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        try:
            from metrics.data.operations.core_models import load_core_data

            load_core_data("source_data/daily_data_alpha_17032023.csv")
            # load_core_data("source_data/sample_data.csv")
        except Exception as e:
            self.stderr.write(f"Uh oh, Data Loader failed: {str(e)}")
        else:
            self.stdout.write("Data Loaded successfully")
