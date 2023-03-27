"""
This file contains the custom QuerySet and Manager classes associated with the `TimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
import datetime

from django.db import models

from metrics.api import enums


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
        self, topic: str, metric: str, date_from: datetime.datetime
    ) -> models.QuerySet:
        queryset = self.filter(
            metric__topic__name=topic,
            metric__name=metric,
            dt__gte=date_from,
        ).values_list("dt", "metric_value")

        return self._oldest_to_newest(queryset=queryset)

    def by_topic_metric_ordered_from_newest_to_oldest(
        self, topic: str, metric: str
    ) -> models.QuerySet:
        queryset = self.filter(
            metric__topic__name=topic,
            metric__name=metric,
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
        self, topic: str, metric: str
    ) -> CoreTimeSeriesQuerySet:
        return self.get_queryset().by_topic_metric_ordered_from_newest_to_oldest(
            topic=topic, metric=metric
        )

    def get_latest_metric_value(
        self, topic: str, metric: str
    ) -> CoreTimeSeriesQuerySet:
        return (
            self.get_queryset()
            .by_topic_metric_ordered_from_newest_to_oldest(topic=topic, metric=metric)
            .first()
        )

    def by_topic_metric_for_dates_and_values(
        self, topic: str, metric: str, date_from: datetime.datetime
    ) -> CoreTimeSeriesQuerySet:
        return self.get_queryset().by_topic_metric_for_dates_and_values(
            topic=topic,
            metric=metric,
            date_from=date_from,
        )
