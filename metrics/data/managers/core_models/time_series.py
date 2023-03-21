"""
This file contains the custom QuerySet and Manager classes associated with the `TimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models

from metrics.api import enums


class CoreTimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `TimeSeriesManager`"""

    def filter_weekly(self) -> models.QuerySet:
        """Filters for all `TimeSeries` records which are of `W` (weekly) period type.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the `TimeSeries` records which have a `W` as the `period` field

        """
        return self.filter(period=enums.TimePeriod.Weekly.value).order_by("start_date")

    def all_related(self) -> models.QuerySet:
        return self.prefetch_related("metric", "geography", "stratum").all()


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
