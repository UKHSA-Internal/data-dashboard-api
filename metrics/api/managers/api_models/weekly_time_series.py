"""
This file contains the custom QuerySet and Manager classes associated with the `WeeklyTimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class WeeklyTimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `WeeklyTimeSeriesManager`"""

    def filter_weekly_positivity_by_topic(self, topic: str) -> models.QuerySet:
        """Filters by the given `topic` for the metric: `weekly_positivity`

        Args:
            topic: The name of the disease being queried.
                E.g. `Influenza`

        Returns:
            QuerySet: An ordered queryset from oldest -> newest

        """
        return self.filter(topic=topic, metric="weekly_positivity", year=2022).order_by(
            "start_date"
        )

    def get_metric_values_for_weekly_positivity_by_topic(
        self, topic: str
    ) -> models.QuerySet:
        """Filters the associated metric_values by the given `topic` for the metric `weekly_positivity`

        Args:
            topic: The name of the disease being queried.
                E.g. `Influenza`

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the individual metric_value numbers:
                Examples:
                    `<QuerySet [33388.0, 5.5, 29214.0, 4.7, 24036.0, 3.9>`

        """
        queryset = self.filter_weekly_positivity_by_topic(topic=topic)
        return queryset.values_list("metric_value", flat=True)


class WeeklyTimeSeriesManager(models.Manager):
    """Custom model manager class for the `WeeklyTimeSeries` model."""

    def get_queryset(self) -> WeeklyTimeSeriesQuerySet:
        return WeeklyTimeSeriesQuerySet(model=self.model, using=self.db)

    def get_metric_values_for_weekly_positivity_by_topic(
        self, topic: str
    ) -> WeeklyTimeSeriesQuerySet:
        """Filters the associated metric_values by the given `topic` for the metric `weekly_positivity`

        Args:
            topic: The name of the disease being queried.
                E.g. `Influenza`

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the individual metric_value numbers:
                Examples:
                    `<QuerySet [33388.0, 5.5, 29214.0, 4.7, 24036.0, 3.9>`

        """
        return self.get_queryset().get_metric_values_for_weekly_positivity_by_topic(
            topic=topic
        )
