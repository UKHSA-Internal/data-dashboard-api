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
        topic: str,
        metric: str,
        upper_confidence: float = None,
        metric_value: int = None,
        lower_confidence: float = None,
        geography: str | None = None,
        geography_type: str | None = None,
        geography_code: str | None = None,
        stratum: str | None = None,
        sex: str | None = None,
        age: str | None = None,
        period_end: str | datetime.date | None = None,
        period_start: str | datetime.date | None = None,
        refresh_date: str | datetime.date | None = None,
        embargo: str | datetime.date | None = None,
    ) -> list[FakeCoreHeadline]:
        geography: FakeGeography = FakeGeographyFactory.build_example(
            geography_type_name=geography_type,
            geography_name=geography,
            geography_code=geography_code,
        )

        stratum: FakeStratum = FakeStratumFactory.build_example(stratum_name=stratum)
        age: FakeAge = FakeAgeFactory.build_example(age_name=age)

        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric,
            metric_group_name="headline",
            topic_name=topic,
        )
        metric_value: int = metric_value or cls._pick_random_positive_metric_value()
        upper_confidence: float = upper_confidence or None
        lower_confidence: float = lower_confidence or None

        return cls.build(
            sex=sex,
            metric_value=metric_value,
            upper_confidence=upper_confidence,
            metric=metric,
            lower_confidence=lower_confidence,
            geography=geography,
            stratum=stratum,
            age=age,
            period_start=period_start,
            period_end=period_end,
            refresh_date=refresh_date,
            embargo=embargo,
        )

    @classmethod
    def build_example_trend_type_records(
        cls,
        topic: str,
        metric: str,
        percentage_metric: str,
        period_end: str | datetime.date,
        geography: str | None = None,
        geography_type: str | None = None,
        stratum: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ) -> list[FakeCoreHeadline]:
        main_metric_headline = cls.build_record(
            topic=topic,
            metric=metric,
            period_end=period_end,
            geography=geography,
            geography_type=geography_type,
            stratum=stratum,
            sex=sex,
            age=age,
        )
        percentage_metric_headline = cls.build_record(
            topic=topic,
            metric=percentage_metric,
            period_end=period_end,
            geography=geography,
            geography_type=geography_type,
            stratum=stratum,
            sex=sex,
            age=age,
        )

        return [main_metric_headline, percentage_metric_headline]
