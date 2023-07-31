import datetime

import pytest

from metrics.data.models.core_models import CoreTimeSeries, Metric, MetricGroup, Topic


@pytest.fixture
def core_headline_example() -> CoreTimeSeries:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="deaths", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_newtests_7daycounttotal",
        metric_group=metric_group,
        topic=topic,
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
def core_trend_percentage_example() -> list[CoreTimeSeries]:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="deaths", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7daychange",
        metric_group=metric_group,
        topic=topic,
    )
    percentage_metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7daypercentchange",
        metric_group=metric_group,
        topic=topic,
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
def core_timeseries_example() -> list[CoreTimeSeries]:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="deaths", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_deaths_ONSByDay",
        metric_group=metric_group,
        topic=topic,
    )
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
