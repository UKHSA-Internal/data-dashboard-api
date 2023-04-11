import datetime
import random
from typing import List

import factory

from .core_time_series import FakeCoreTimeSeries
from .metric import FakeMetric
from .topic import FakeTopic


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
        cls, dt: datetime.date, metric_name: str, topic_name: str
    ) -> FakeCoreTimeSeries:
        metric: FakeMetric = cls._build_example_metric(
            metric_name=metric_name, topic_name=topic_name
        )
        return cls.build(
            period="D",
            sex="ALL",
            year=dt.year,
            metric_value=1,
            metric=metric,
            dt=dt,
        )

    @classmethod
    def build_example_covid_time_series_range(cls) -> List[FakeCoreTimeSeries]:
        time_series_range = []

        metric: FakeMetric = cls._build_example_metric()

        for month_number in range(4, 10, 1):
            for day_number in (3, 16, 28):
                metric_value = random.choice(range(100, 20100, 100))

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
