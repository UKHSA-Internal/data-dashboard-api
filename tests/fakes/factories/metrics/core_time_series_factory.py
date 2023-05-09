import datetime
import secrets
from typing import List

import factory

from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.stratum_factory import FakeStratumFactory
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries
from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.stratum import FakeStratum
from tests.fakes.models.metrics.topic import FakeTopic


class FakeCoreTimeSeriesFactory(factory.Factory):
    """
    Factory for creating `FakeCoreTimeSeries` instances for tests
    """

    class Meta:
        model = FakeCoreTimeSeries

    @classmethod
    def _build_example_metric(
        cls, metric_name: str = "new_cases_daily", topic_name: str = "COVID-19"
    ) -> FakeMetric:
        topic = FakeTopic(name=topic_name)
        return FakeMetric(name=metric_name, topic=topic)

    @classmethod
    def build_time_series(
        cls,
        dt: datetime.date,
        metric_name: str,
        topic_name: str,
        stratum_name: str = "",
    ) -> FakeCoreTimeSeries:
        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name, topic_name=topic_name
        )
        if stratum_name:
            stratum: FakeStratum = FakeStratumFactory.build_example(
                stratum_name=stratum_name,
            )
        else:
            stratum = None

        return cls.build(
            period="D",
            sex="ALL",
            year=dt.year,
            metric_value=1,
            metric=metric,
            dt=dt,
            stratum=stratum,
        )

    @classmethod
    def build_example_covid_time_series_range(cls) -> List[FakeCoreTimeSeries]:
        time_series_range = []

        metric: FakeMetric = cls._build_example_metric()

        for month_number in range(4, 10, 1):
            for day_number in (3, 16, 28):
                metric_value = cls._pick_random_positive_metric_value()

                new_time_series = cls.build(
                    period="D",
                    sex="ALL",
                    year=2023,
                    dt=datetime.date(year=2023, month=month_number, day=day_number),
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
    ) -> List[FakeCoreTimeSeries]:
        time_series_records = []

        metric: FakeMetric = cls._build_example_metric(metric_name=metric_name)
        metric_value: int = cls._pick_random_positive_metric_value()

        percentage_metric: FakeMetric = cls._build_example_metric(
            metric_name=percentage_metric_name
        )
        percentage_metric_value: float = cls._pick_random_percentage_value()

        metric_time_series = cls.build(
            period="D",
            sex="ALL",
            year=2023,
            dt=datetime.date(year=2023, month=1, day=1),
            metric_value=metric_value,
            metric=metric,
        )
        time_series_records.append(metric_time_series)

        metric_time_series = cls.build(
            period="D",
            sex="ALL",
            year=2023,
            dt=datetime.date(year=2023, month=1, day=1),
            metric_value=percentage_metric_value,
            metric=percentage_metric,
        )
        time_series_records.append(metric_time_series)

        return time_series_records
