import datetime
import random

import factory

from tests.fakes.models.core_time_series import FakeCoreTimeSeries


class FakeCoreTimeSeriesFactory(factory.Factory):
    """
    Factory for creating `FakeCoreTimeSeries` instances for tests
    """

    class Meta:
        model = FakeCoreTimeSeries

    @classmethod
    def build_example_time_series_range(cls) -> FakeCoreTimeSeries:
        time_series_range = []

        for month_number in range(4, 10, 1):
            for day_number in (3, 16, 28):

                metric_value = random.choice(range(100, 20100, 100))

                new_time_series = cls.build(
                    period="D",
                    sex="ALL",
                    year=2023,
                    dt=datetime.date(year=2023, month=month_number, day=day_number),
                    metric_value=metric_value,
                )
                time_series_range.append(new_time_series)

        return time_series_range