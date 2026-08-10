import datetime
import pytest
from django.utils import timezone
from unittest import mock

from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    CoreTimeSeries,
    Metric,
    MetricGroup,
    Topic,
)

from tests.factories.common.auth.permissions import UserPermissionsFactory
from tests.factories.metrics.headline import CoreHeadlineFactory


@pytest.fixture(
    params=[
        pytest.param({"is_public": False}, id="non_public"),
        pytest.param({"is_public": True}, id="public"),
    ]
)
def core_headline_example(request) -> CoreHeadline:
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
        is_public=request.param["is_public"],
    )


@pytest.fixture(
    params=[
        pytest.param({"is_public": False}, id="non_public"),
        pytest.param({"is_public": True}, id="public"),
    ]
)
def core_trend_example(request) -> tuple[CoreHeadline, CoreHeadline]:
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
        is_public=request.param["is_public"],
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
        is_public=request.param["is_public"],
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


@pytest.fixture
def user_global_access() -> dict:
    mock_user = mock.MagicMock()
    mock_user.username = "restricted-user"

    mock_user.permission_sets = UserPermissionsFactory(
        [],
        has_global_access=True,
    )
    return mock_user
