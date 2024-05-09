import datetime
import secrets

import factory

from tests.fakes.factories.metrics.age_factory import FakeAgeFactory
from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.stratum_factory import FakeStratumFactory
from tests.fakes.models.metrics.age import FakeAge
from tests.fakes.models.metrics.geography import FakeGeography
from tests.fakes.models.metrics.headline import FakeCoreHeadline
from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.stratum import FakeStratum


class FakeCoreHeadlineFactory(factory.Factory):
    """
    Factory for creating `FakeCoreHeadline` instances for tests
    """

    class Meta:
        model = FakeCoreHeadline

    @classmethod
    def _pick_random_percentage_value(cls) -> float:
        random_integer = secrets.choice(range(-100_000, 100_000))
        return random_integer / 100

    @classmethod
    def _pick_random_positive_metric_value(cls) -> int:
        return secrets.randbelow(100)

    @classmethod
    def build_record(
        cls,
        topic_name: str,
        metric_name: str,
        metric_value: int = None,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        geography_code: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
        period_end: str | datetime.date | None = None,
        period_start: str | datetime.date | None = None,
        refresh_date: str | datetime.date | None = None,
    ) -> list[FakeCoreHeadline]:
        geography: FakeGeography = FakeGeographyFactory.build_example(
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            geography_code=geography_code,
        )

        stratum: FakeStratum = FakeStratumFactory.build_example(
            stratum_name=stratum_name
        )
        age: FakeAge = FakeAgeFactory.build_example(age_name=age)

        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name,
            metric_group_name="headline",
            topic_name=topic_name,
        )
        metric_value: int = metric_value or cls._pick_random_positive_metric_value()

        return cls.build(
            sex=sex,
            metric_value=metric_value,
            metric=metric,
            geography=geography,
            stratum=stratum,
            age=age,
            period_start=period_start,
            period_end=period_end,
            refresh_date=refresh_date,
        )

    @classmethod
    def build_example_trend_type_records(
        cls,
        topic_name: str,
        metric_name: str,
        percentage_metric_name: str,
        period_end: str | datetime.date,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ) -> list[FakeCoreHeadline]:
        headline_records = []

        geography: FakeGeography = FakeGeographyFactory.build_example(
            geography_type_name=geography_type_name,
            geography_name=geography_name,
        )

        stratum: FakeStratum = FakeStratumFactory.build_example(
            stratum_name=stratum_name
        )
        age: FakeAge = FakeAgeFactory.build_example(age_name=age)

        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name,
            metric_group_name="headline",
            topic_name=topic_name,
        )
        metric_value: int = cls._pick_random_positive_metric_value()

        percentage_metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=percentage_metric_name,
            metric_group_name="headline",
            topic_name=topic_name,
        )
        percentage_metric_value: float = cls._pick_random_percentage_value()

        metric_time_series = cls.build(
            sex=sex,
            metric_value=metric_value,
            metric=metric,
            geography=geography,
            stratum=stratum,
            age=age,
            period_end=period_end,
        )
        headline_records.append(metric_time_series)

        metric_time_series = cls.build(
            sex=sex,
            metric_value=percentage_metric_value,
            metric=percentage_metric,
            geography=geography,
            stratum=stratum,
            age=age,
            period_end=period_end,
        )
        headline_records.append(metric_time_series)

        return headline_records
