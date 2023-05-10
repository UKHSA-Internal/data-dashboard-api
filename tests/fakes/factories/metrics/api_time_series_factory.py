import datetime

import factory

from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


class FakeAPITimeSeriesFactory(factory.Factory):
    """
    Factory for creating `FakeAPITimeSeries` instances for tests
    """

    class Meta:
        model = FakeAPITimeSeries

    @classmethod
    def build_example_covid_time_series(cls) -> FakeAPITimeSeries:
        return cls.build(
            period="D",
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
            geography_type="Nation",
            geography="England",
            metric="new_cases_daily",
            stratum="default",
            sex="ALL",
            year=2023,
            epiweek=10,
            dt=datetime.date(year=2023, month=3, day=8),
            metric_value=2364,
        )

    @classmethod
    # Sample model with some fields missing
    def build_example_api_time_series_fields_missing(cls) -> FakeAPITimeSeries:
        return cls.build(
            period="D",
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
            metric="new_cases_daily",
            stratum="default",
            dt=datetime.date(year=2023, month=3, day=8),
            metric_value=2364,
        )
