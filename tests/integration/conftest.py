import datetime

import pytest

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


@pytest.fixture
def core_headline_example() -> CoreTimeSeries:
    topic, _ = Topic.objects.get_or_create(name="COVID-19")
    metric_group, _ = MetricGroup.objects.get_or_create(
        name="deaths", topic_id=topic.id
    )
    metric, _ = Metric.objects.get_or_create(
        name="COVID-19_headline_tests_7DayTotals",
        metric_group_id=metric_group.id,
        topic_id=topic.id,
    )
    year = 2023
    return CoreTimeSeries.objects.create(
        metric_value=123,
        metric=metric,
        year=year,
        epiweek=1,
        date=datetime.date(year=year, month=1, day=1),
    )


@pytest.fixture
def core_headline_example_beta() -> CoreHeadline:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="headline", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_tests_7DayTotals",
        metric_group=metric_group,
        topic=topic,
    )
    geography_type = GeographyType.objects.create(name="Nation")
    geography = Geography.objects.create(name="England", geography_type=geography_type)
    return CoreHeadline.objects.create(
        metric_value=123,
        metric=metric,
        geography=geography,
        refresh_date="2023-01-07",
        period_start="2023-01-01",
        period_end="2023-01-07",
    )


@pytest.fixture
def core_trend_example_beta() -> tuple[CoreHeadline, CoreHeadline]:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="headline", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7DayChange",
        metric_group=metric_group,
        topic=topic,
    )
    percentage_metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7DayPercentChange",
        metric_group=metric_group,
        topic=topic,
    )

    geography_type = GeographyType.objects.create(name="Nation")
    geography = Geography.objects.create(name="England", geography_type=geography_type)

    main_timeseries = CoreHeadline.objects.create(
        metric_value=123,
        metric=metric,
        geography=geography,
        refresh_date="2023-01-07",
        period_start="2023-01-01",
        period_end="2023-01-07",
    )
    percentage_timeseries = CoreHeadline.objects.create(
        metric_value=3,
        metric=percentage_metric,
        geography=geography,
        refresh_date="2023-01-07",
        period_start="2023-01-01",
        period_end="2023-01-07",
    )
    return main_timeseries, percentage_timeseries


@pytest.fixture
def core_trend_percentage_example() -> list[CoreTimeSeries]:
    topic = Topic.objects.create(name="COVID-19")
    metric_group = MetricGroup.objects.create(name="deaths", topic=topic)
    metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7DayChange",
        metric_group=metric_group,
        topic=topic,
    )
    percentage_metric = Metric.objects.create(
        name="COVID-19_headline_ONSdeaths_7DayPercentChange",
        metric_group=metric_group,
        topic=topic,
    )

    year = 2023

    main_timeseries: CoreTimeSeries = CoreTimeSeries.objects.create(
        metric_value=123,
        metric=metric,
        year=year,
        epiweek=1,
        date=datetime.date(year=year, month=1, day=1),
    )
    percentage_timeseries: CoreTimeSeries = CoreTimeSeries.objects.create(
        metric_value=3,
        metric=percentage_metric,
        year=year,
        epiweek=1,
        date=datetime.date(year=year, month=1, day=1),
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
    age = Age.objects.create(name="all")
    year = 2023
    return [
        CoreTimeSeries.objects.create(
            metric_value=123,
            metric=metric,
            age=age,
            year=year,
            epiweek=1,
            date=datetime.date(year=year, month=1, day=i + 1),
            refresh_date=datetime.date(year=year, month=1, day=10),
        )
        for i in range(2)
    ]
