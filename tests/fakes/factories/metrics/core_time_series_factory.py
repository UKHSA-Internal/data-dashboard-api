import datetime
import secrets

import factory

from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.stratum_factory import FakeStratumFactory
from tests.fakes.models.metrics.age import FakeAge
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries
from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.stratum import FakeStratum


class FakeCoreTimeSeriesFactory(factory.Factory):
    """
    Factory for creating `FakeCoreTimeSeries` instances for tests
    """

    class Meta:
        model = FakeCoreTimeSeries

    @classmethod
    def build_time_series(
        cls,
        date: datetime.date,
        metric_name: str,
        topic_name: str,
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        age_name: str = "all",
        sex: str = "all",
        stratum_name: str = "default",
        metric_value: float = 1,
        epiweek: int = 1,
        in_reporting_lag_period: bool = False,
    ) -> FakeCoreTimeSeries:
        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name,
            topic_name=topic_name,
        )

        geography = FakeGeographyFactory.build_example(
            geography_name=geography_name, geography_type_name=geography_type_name
        )

        stratum: FakeStratum = FakeStratumFactory.build_example(
            stratum_name=stratum_name,
        )

        age = FakeAge(name=age_name)

        return cls.build(
            metric_frequency="D",
            year=date.year,
            metric_value=metric_value,
            metric=metric,
            geography=geography,
            date=date,
            stratum=stratum,
            age=age,
            sex=sex,
            epiweek=epiweek,
            refresh_date=str(date),
            in_reporting_lag_period=in_reporting_lag_period,
        )

    @classmethod
    def build_example_covid_time_series_range(cls) -> list[FakeCoreTimeSeries]:
        time_series_range = []

        metric: FakeMetric = FakeMetricFactory.build_example_metric()

        for month_number in range(4, 10, 1):
            for day_number in (3, 16, 28):
                metric_value = cls._pick_random_positive_metric_value()

                new_time_series = cls.build(
                    metric_frequency="D",
                    sex="ALL",
                    year=2023,
                    date=datetime.date(year=2023, month=month_number, day=day_number),
                    metric_value=metric_value,
                    metric=metric,
                )
                time_series_range.append(new_time_series)

        return time_series_range

    @classmethod
    def _pick_random_percentage_value(cls) -> float:
        random_integer = secrets.choice(range(-100_000, 100_000))
        return random_integer / 100

    @classmethod
    def _pick_random_positive_metric_value(cls) -> int:
        return secrets.randbelow(100)

    @classmethod
    def build_example_trend_type_records(
        cls, metric_name: str, percentage_metric_name: str
    ) -> list[FakeCoreTimeSeries]:
        time_series_records = []

        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name
        )
        metric_value: int = cls._pick_random_positive_metric_value()

        percentage_metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=percentage_metric_name
        )
        percentage_metric_value: float = cls._pick_random_percentage_value()

        metric_time_series = cls.build(
            metric_frequency="D",
            sex="ALL",
            year=2023,
            date=datetime.date(year=2023, month=1, day=1),
            metric_value=metric_value,
            metric=metric,
        )
        time_series_records.append(metric_time_series)

        metric_time_series = cls.build(
            metric_frequency="D",
            sex="ALL",
            year=2023,
            date=datetime.date(year=2023, month=1, day=1),
            metric_value=percentage_metric_value,
            metric=percentage_metric,
        )
        time_series_records.append(metric_time_series)

        return time_series_records
