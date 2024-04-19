import contextlib
import datetime

import factory
from django.utils import timezone
from metrics.data.models.api_models import APITimeSeries


class APITimeSeriesFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `APITimeSeries` instances for tests
    """

    class Meta:
        model = APITimeSeries

    @classmethod
    def create_record(
        cls,
        metric_value: float = 123.456,
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
        topic_name: str = "COVID-19",
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        geography_code: str = "E92000001",
        metric_name: str = "COVID-19_cases_casesByDay",
        metric_frequency: str = "D",
        stratum_name: str = "default",
        age_name: str = "all",
        sex: str = "all",
        year: int = 2023,
        epiweek: int = 1,
        refresh_date: str | datetime.datetime = datetime.datetime(2023, 8, 10),
        date: str | datetime.date = "2023-01-01",
        embargo: str | datetime.datetime = datetime.datetime(2024, 4, 10),
        **kwargs
    ):
        refresh_date: datetime.datetime = cls._make_datetime_timezone_aware(
            datetime_obj=refresh_date
        )
        embargo: datetime.datetime = cls._make_datetime_timezone_aware(
            datetime_obj=embargo
        )

        return cls.create(
            metric_value=metric_value,
            metric_frequency=metric_frequency,
            metric=metric_name,
            geography=geography_name,
            geography_code=geography_code,
            geography_type=geography_type_name,
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            stratum=stratum_name,
            age=age_name,
            sex=sex,
            year=year,
            month=1,
            epiweek=epiweek,
            date=date,
            refresh_date=refresh_date,
            embargo=embargo,
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
