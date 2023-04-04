"""
This file contains the custom QuerySet and Manager classes associated with the `CoreTimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
import datetime
import logging
from typing import Union

from django.db import models

from metrics.api import enums

logger = logging.getLogger(__name__)


class CoreTimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreTimeSeriesManager`"""

    def filter_weekly(self) -> models.QuerySet:
        """Filters for all `TimeSeries` records which are of `W` (weekly) period type.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the `TimeSeries` records which have a `W` as the `period` field

        """
        return self.filter(period=enums.TimePeriod.Weekly.value).order_by("start_date")

    def all_related(self) -> models.QuerySet:
        return self.prefetch_related("metric", "geography", "stratum").all()

    @staticmethod
    def _newest_to_oldest(queryset: models.QuerySet) -> models.QuerySet:
        return queryset.order_by("-dt")

    @staticmethod
    def _oldest_to_newest(queryset: models.QuerySet) -> models.QuerySet:
        return queryset.order_by("dt")

    def by_topic_metric_for_dates_and_values(
        self, topic: str, metric_name: str, date_from: datetime.datetime
    ) -> models.QuerySet:
        """Filters by the given `topic` and `metric`. Slices all values older than the `date_from`.

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `new_cases_daily
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        queryset = self.filter(
            metric__topic__name=topic,
            metric__name=metric_name,
            dt__gte=date_from,
        ).values_list("dt", "metric_value")

        return self._oldest_to_newest(queryset=queryset)

    def by_topic_metric_ordered_from_newest_to_oldest(
        self, topic: str, metric_name: str
    ) -> models.QuerySet:
        """Filters by the given `topic` and `metric`. Slices all values older than the `date_from`.

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `new_cases_daily

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the individual metric_value numbers only:
                Examples:
                    `<CoreTimeSeriesQuerySet [ Decimal('0.8'), Decimal('0.9')]>`

        """
        queryset = self.filter(
            metric__topic__name=topic,
            metric__name=metric_name,
        ).values_list("metric_value", flat=True)
        return self._newest_to_oldest(queryset=queryset)


class CoreTimeSeriesManager(models.Manager):
    """Custom model manager class for the `TimeSeries` model."""

    def get_queryset(self) -> CoreTimeSeriesQuerySet:
        return CoreTimeSeriesQuerySet(model=self.model, using=self.db)

    def filter_weekly(self) -> CoreTimeSeriesQuerySet:
        """Filters for all `TimeSeries` records which are of `W` (weekly) period type.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the `TimeSeries` records which have a `W` as the `period` field

        """
        return self.get_queryset().filter_weekly()

    def all_related(self) -> CoreTimeSeriesQuerySet:
        return self.get_queryset().all_related()

    def by_topic_metric_ordered_from_newest(
        self, topic: str, metric_name: str
    ) -> CoreTimeSeriesQuerySet:
        """Filters by the given `topic` and `metric`. Slices all values older than the `date_from`.

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `new_cases_daily

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the individual metric_value numbers only:
                Examples:
                    `<CoreTimeSeriesQuerySet [Decimal('0.8'), Decimal('0.9')]>`

        """
        return self.get_queryset().by_topic_metric_ordered_from_newest_to_oldest(
            topic=topic, metric_name=metric_name
        )

    def get_latest_metric_value(
        self, topic: str, metric_name: str
    ) -> Union[int, float]:
        """Grabs by the latest record by the given `topic` and `metric`.

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `new_cases_daily

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the individual metric_value numbers only:
                Examples:
                    `0.8`

        """
        return (
            self.get_queryset()
            .by_topic_metric_ordered_from_newest_to_oldest(
                topic=topic, metric_name=metric_name
            )
            .first()
        )

    def by_topic_metric_for_dates_and_values(
        self, topic: str, metric_name: str, date_from: datetime.datetime
    ) -> CoreTimeSeriesQuerySet:
        """Filters by the given `topic` and `metric`. Slices all values older than the `date_from`.

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `new_cases_daily
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        return self.get_queryset().by_topic_metric_for_dates_and_values(
            topic=topic,
            metric_name=metric_name,
            date_from=date_from,
        )
