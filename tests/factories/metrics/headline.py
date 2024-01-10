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
)


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
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
        topic_name: str = "COVID-19",
        metric_name: str = "COVID-19_headline_positivity_latest",
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        stratum_name: str = "default",
        age_name: str = "all",
        sex: str = "all",
        refresh_date: str | datetime.date = "2023-10-01",
        period_start: str | datetime.date = "2023-01-01",
        period_end: str | datetime.date = "2023-01-07",
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
            **kwargs
        )
