import contextlib
import datetime

import factory

from metrics.data.models.core_models import (
    Age,
    CoreTimeSeries,
    Geography,
    GeographyType,
    Metric,
    Stratum,
    SubTheme,
    Theme,
    Topic,
)
from django.utils import timezone


class CoreTimeSeriesFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `CoreTimeSeries` instances for tests
    """

    class Meta:
        model = CoreTimeSeries

    @classmethod
    def create_record(
        cls,
        metric_value: float = 123.456,
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
        topic_name: str = "COVID-19",
        metric_name: str = "COVID-19_cases_casesByDay",
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        stratum_name: str = "default",
        age_name: str = "all",
        sex: str = "all",
        year: int = 2023,
        epiweek: int = 1,
        date: str | datetime.date = "2023-01-01",
        refresh_date: str | datetime.datetime = datetime.datetime(2024, 4, 19),
        **kwargs
    ):
        theme, _ = Theme.objects.get_or_create(name=theme_name)
        sub_theme, _ = SubTheme.objects.get_or_create(
            name=sub_theme_name, theme_id=theme.id
        )
        topic, _ = Topic.objects.get_or_create(
            name=topic_name, sub_theme_id=sub_theme.id
        )
        metric, _ = Metric.objects.get_or_create(name=metric_name, topic_id=topic.id)

        geography_type, _ = GeographyType.objects.get_or_create(
            name=geography_type_name
        )
        geography, _ = Geography.objects.get_or_create(
            name=geography_name, geography_type_id=geography_type.id
        )
        age, _ = Age.objects.get_or_create(name=age_name)
        stratum, _ = Stratum.objects.get_or_create(name=stratum_name)
        refresh_date: datetime.datetime = cls._make_datetime_timezone_aware(
            datetime_obj=refresh_date
        )

        return cls.create(
            metric=metric,
            metric_frequency="D",
            geography=geography,
            stratum=stratum,
            age=age,
            sex=sex,
            metric_value=metric_value,
            year=year,
            month=1,
            epiweek=epiweek,
            date=date,
            refresh_date=refresh_date,
            **kwargs
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
