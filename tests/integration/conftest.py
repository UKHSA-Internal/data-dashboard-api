import datetime
import os
import importlib
from unittest import mock

import pytest
from django.utils import timezone

from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    CoreTimeSeries,
    Geography,
    GeographyType,
    Metric,
    MetricGroup,
    Topic,
)

from metrics.api.settings import private_api


@pytest.fixture
def core_headline_example() -> CoreHeadline:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="headline", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_tests_7DayTotals",
        metric_group=metric_group,
        topic=topic,
    )
    geography_type = GeographyType.objects.create(name="Nation")
    geography = Geography.objects.create(name="England", geography_type=geography_type)

    refresh_date: datetime.datetime = timezone.make_aware(
        value=datetime.datetime(year=2023, month=1, day=7)
    )
    return CoreHeadline.objects.create(
        metric_value=123.0000,
        metric=metric,
        geography=geography,
        sex="f",
        refresh_date=refresh_date,
        period_start="2023-01-01",
        period_end="2023-01-07",
    )


@pytest.fixture
def core_trend_example() -> tuple[CoreHeadline, CoreHeadline]:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="headline", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_cases_7DayChange",
        metric_group=metric_group,
        topic=topic,
    )
    percentage_metric = Metric.objects.create(
        name="COVID-19_headline_cases_7DayPercentChange",
        metric_group=metric_group,
        topic=topic,
    )

    geography_type = GeographyType.objects.create(name="Nation")
    geography = Geography.objects.create(name="England", geography_type=geography_type)

    period_end: datetime.datetime = timezone.make_aware(
        value=datetime.datetime(year=2023, month=1, day=7)
    )

    refresh_date: datetime.datetime = timezone.make_aware(
        value=datetime.datetime(year=2023, month=1, day=7)
    )
    main_timeseries = CoreHeadline.objects.create(
        metric_value=123.0,
        metric=metric,
        geography=geography,
        refresh_date=refresh_date,
        period_start="2023-01-01",
        period_end=period_end,
    )
    percentage_timeseries = CoreHeadline.objects.create(
        metric_value=3.0,
        metric=percentage_metric,
        geography=geography,
        refresh_date=refresh_date,
        period_start="2023-01-01",
        period_end=period_end,
    )
    return main_timeseries, percentage_timeseries


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
