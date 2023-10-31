import datetime

import factory

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
        refresh_date: str | datetime.date = "2023-08-10",
        date: str | datetime.date = "2023-01-01",
        **kwargs
    ):
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
            epiweek=epiweek,
            date=date,
            refresh_date=refresh_date,
            **kwargs
        )
