"""
For any given API we will require:
 - An API View
 - Flat model generated from the core data
 - Function to generate the flat model from the core data

This file contains the flat models only.
Note that the flat models should only be populated
    via the `generate_weekly_time_series()` function not through any API route.
"""
from django.db import models


class WeeklyTimeSeries(models.Model):
    theme = models.CharField(max_length=30)
    sub_theme = models.CharField(max_length=30)
    topic = models.CharField(max_length=30)

    geography_type = models.CharField(max_length=30)
    geography = models.CharField(max_length=30)

    metric = models.CharField(max_length=30)

    stratum = models.CharField(max_length=30)
    year = models.IntegerField()
    epiweek = models.IntegerField()
    start_date = models.DateField(max_length=30)

    metric_value = models.FloatField(max_length=30)

    def __str__(self):
        return f"Data for {self.start_date}, metric '{self.metric}', stratum '{self.stratum}', value: {self.metric_value}"


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
        return self.get_metric_values_for_weekly_positivity_by_topic(topic=topic)
