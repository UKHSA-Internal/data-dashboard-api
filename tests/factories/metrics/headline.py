import contextlib
import datetime

import factory

from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    Geography,
    GeographyType,
    Metric,
    Stratum,
    SubTheme,
    Theme,
    Topic,
    MetricGroup,
)
from django.utils import timezone


class CoreHeadlineFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `CoreHeadline` instances for tests
    """

    class Meta:
        model = CoreHeadline

    @classmethod
    def create_record(
        cls,
        metric_value: float = 123.456,
        theme: str = "infectious_disease",
        sub_theme: str = "respiratory",
        topic: str = "COVID-19",
        metric: str = "COVID-19_headline_positivity_latest",
        metric_group: str = "headline",
        geography: str = "England",
        geography_type: str = "Nation",
        geography_code: str = "E92000001",
        stratum: str = "default",
        age: str = "all",
        sex: str = "all",
        refresh_date: str | datetime.datetime = datetime.datetime(2023, 10, 1),
        period_start: str | datetime.date = "2023-01-01",
        period_end: str | datetime.date = "2023-01-07",
        embargo: str | datetime.datetime = datetime.datetime(2024, 4, 10),
        upper_confidence: float | None = None,
        lower_confidence: float | None = None,
        is_public: bool = True,
        **kwargs
    ):
        theme, _ = Theme.objects.get_or_create(name=theme)
        sub_theme, _ = SubTheme.objects.get_or_create(name=sub_theme, theme_id=theme.id)
        topic, _ = Topic.objects.get_or_create(name=topic, sub_theme_id=sub_theme.id)
        metric_group, _ = MetricGroup.objects.get_or_create(
            name=metric_group, topic_id=topic.id
        )
        metric, _ = Metric.objects.get_or_create(
            name=metric, topic_id=topic.id, metric_group_id=metric_group.id
        )

        geography_type, _ = GeographyType.objects.get_or_create(name=geography_type)
        geography, _ = Geography.objects.get_or_create(
            name=geography,
            geography_code=geography_code,
            geography_type_id=geography_type.id,
        )
        age, _ = Age.objects.get_or_create(name=age)
        stratum, _ = Stratum.objects.get_or_create(name=stratum)
        refresh_date: datetime.datetime = cls._make_datetime_timezone_aware(
            datetime_obj=refresh_date
        )

        return cls.create(
            metric=metric,
            geography=geography,
            stratum=stratum,
            age=age,
            sex=sex,
            metric_value=metric_value,
            refresh_date=refresh_date,
            period_start=period_start,
            period_end=period_end,
            embargo=embargo,
            is_public=is_public,
            lower_confidence=lower_confidence,
            upper_confidence=upper_confidence,
            **kwargs,
        )

    @classmethod
    def _make_datetime_timezone_aware(
        cls, datetime_obj: str | datetime.datetime | None
    ) -> datetime.datetime:

        if datetime_obj is None:
            return datetime_obj

        with contextlib.suppress(TypeError):
            # If it is already a datetime object then suppress the resulting TypeError
            datetime_obj = datetime.datetime.strptime(datetime_obj, "%Y-%m-%d")

        try:
            return timezone.make_aware(value=datetime_obj)
        except ValueError:
            # The object is already timezone aware
            return datetime_obj
