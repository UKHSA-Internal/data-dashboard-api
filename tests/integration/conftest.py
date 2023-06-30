import datetime
from typing import List

import pytest
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey

from metrics.data.models.core_models import CoreTimeSeries, Metric, Topic


@pytest.fixture
def authenticated_api_client() -> APIClient:
    _, key = APIKey.objects.create_key(name="Test Key")

    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=key)

    return api_client


@pytest.fixture
def core_headline_example() -> CoreTimeSeries:
    topic = Topic.objects.create(name="COVID-19")
    metric = Metric.objects.create(
        name="COVID-19_headline_newtests_7daycounttotal", topic=topic
    )
    year = 2023
    return CoreTimeSeries.objects.create(
        metric_value=123,
        metric=metric,
        year=year,
        epiweek=1,
        dt=datetime.date(year=year, month=1, day=1),
    )


@pytest.fixture
def core_trend_percentage_example() -> List[CoreTimeSeries]:
    topic = Topic.objects.create(name="COVID-19")
    metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7daychange", topic=topic
    )
    percentage_metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7daypercentchange", topic=topic
    )

    year = 2023

    main_timeseries: CoreTimeSeries = CoreTimeSeries.objects.create(
        metric_value=123,
        metric=metric,
        year=year,
        epiweek=1,
        dt=datetime.date(year=year, month=1, day=1),
    )
    percentage_timeseries: CoreTimeSeries = CoreTimeSeries.objects.create(
        metric_value=3,
        metric=percentage_metric,
        year=year,
        epiweek=1,
        dt=datetime.date(year=year, month=1, day=1),
    )
    return [main_timeseries, percentage_timeseries]


@pytest.fixture
def core_timeseries_example() -> List[CoreTimeSeries]:
    topic = Topic.objects.create(name="COVID-19")
    metric = Metric.objects.create(name="COVID-19_deaths_ONSByDay", topic=topic)
    year = 2023
    return [
        CoreTimeSeries.objects.create(
            metric_value=123,
            metric=metric,
            year=year,
            epiweek=1,
            dt=datetime.date(year=year, month=1, day=i + 1),
        )
        for i in range(2)
    ]
