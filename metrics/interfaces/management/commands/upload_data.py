from django.core.management.base import BaseCommand

from metrics.data.models import api_models, core_models
from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data


class Command(BaseCommand):
    @staticmethod
    def _clean_tables():
        models = [
            core_models.CoreTimeSeries,
            core_models.Topic,
            core_models.Metric,
            core_models.Theme,
            core_models.SubTheme,
            core_models.GeographyType,
            core_models.Geography,
            core_models.Stratum,
            api_models.APITimeSeries,
        ]

        for model in models:
            model.objects.all().delete()

    def handle(self, *args, **options) -> None:
        self._clean_tables()
        load_core_data(filename="") # TODO: Add file here
        generate_api_time_series()

