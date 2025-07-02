import datetime
import pytest
from django.utils import timezone

from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    CoreTimeSeries,
    Metric,
    MetricGroup,
    Topic,
)

from tests.factories.metrics.headline import CoreHeadlineFactory


@pytest.fixture
def core_headline_example() -> CoreHeadline:
    refresh_date: datetime.datetime = timezone.make_aware(
        value=datetime.datetime(year=2023, month=1, day=7)
    )
    return CoreHeadlineFactory.create_record(
        metric_value=123.0000,
        metric="COVID-19_headline_tests_7DayTotals",
        topic="COVID-19",
        geography_code="E92000001",
        geography="England",
        geography_type="Nation",
        age="default",
        refresh_date=refresh_date,
        stratum="default",
        sex="f",
        period_start="2023-01-01",
        period_end="2023-01-07",
    )


@pytest.fixture
def core_trend_example() -> tuple[CoreHeadline, CoreHeadline]:
    period_end: datetime.datetime = timezone.make_aware(
        value=datetime.datetime(year=2023, month=1, day=7)
    )
    refresh_date: datetime.datetime = timezone.make_aware(
        value=datetime.datetime(year=2023, month=1, day=7)
    )

    main_metric = CoreHeadlineFactory.create_record(
        metric_value=123.0000,
        metric="COVID-19_headline_cases_7DayChange",
        topic="COVID-19",
        geography_code="E92000001",
        geography="England",
        geography_type="Nation",
        age="default",
        stratum="default",
        sex="f",
        refresh_date=refresh_date,
        period_start="2023-01-01",
        period_end=period_end,
    )

    percentage_metric = CoreHeadlineFactory.create_record(
        metric_value=3.0000,
        metric="COVID-19_headline_cases_7DayPercentChange",
        topic="COVID-19",
        geography_code="E92000001",
        geography="England",
        geography_type="Nation",
        age="default",
        stratum="default",
        sex="f",
        refresh_date=refresh_date,
        period_start="2023-01-01",
        period_end=period_end,
    )

    return main_metric, percentage_metric


@pytest.fixture
def core_timeseries_example() -> list[CoreTimeSeries]:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="deaths", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_deaths_ONSByDay",
        metric_group=metric_group,
        topic=topic,
    )
    age = Age.objects.create(name="all")
    year = 2023
    month = 1
    return [
        CoreTimeSeries.objects.create(
            metric_value=123,
            metric=metric,
            age=age,
            year=year,
            epiweek=1,
            date=datetime.date(year=year, month=month, day=i + 1),
            refresh_date=timezone.make_aware(
                value=datetime.datetime(year=year, month=month, day=10)
            ),
        )
        for i in range(2)
    ]


@pytest.fixture
def patch_auth_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "1")


@pytest.fixture
def patch_auth_disabled(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "0")
