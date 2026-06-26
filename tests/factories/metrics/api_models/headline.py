import contextlib
import datetime

import factory
from django.utils import timezone
from metrics.data.models.api_models import APIHeadline


class APIHeadlineFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `APIHeadline` instances for tests
    """

    class Meta:
        model = APIHeadline

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
        refresh_date: datetime.datetime = cls._make_datetime_timezone_aware(
            datetime_obj=refresh_date
        )
        embargo: datetime.datetime = cls._make_datetime_timezone_aware(
            datetime_obj=embargo
        )

        return cls.create(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric_value=metric_value,
            metric=metric,
            metric_group=metric_group,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            age=age,
            sex=sex,
            period_start=period_start,
            period_end=period_end,
            embargo=embargo,
            upper_confidence=upper_confidence,
            lower_confidence=lower_confidence,
            is_public=is_public,
            refresh_date=refresh_date,
            **kwargs
        )

    @classmethod
    def _make_datetime_timezone_aware(
        cls, datetime_obj: str | datetime.datetime | None
    ) -> datetime.datetime:

        if datetime_obj.tzinfo is None:
            return datetime_obj

        with contextlib.suppress(ValueError):
            datetime_obj = datetime.datetime.strptime(datetime_obj, "%Y-%m-%d")

        try:
            return timezone.make_aware(value=datetime_obj)
        except ValueError:
            # The object is already timezone aware
            return datetime_obj
