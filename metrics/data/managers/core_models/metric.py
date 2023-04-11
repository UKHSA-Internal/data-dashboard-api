"""
This file contains the custom QuerySet and Manager classes associated with the `Metric` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models


class MetricQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `MetricManager`"""

    def get_all_names(self) -> models.QuerySet:
        return self.all().values_list("name", flat=True)

    def is_metric_available_for_topic(
        self, metric_name: str, topic_name: str
    ) -> models.QuerySet:
        return self.filter(name=metric_name, topic__name=topic_name).exists()


class MetricManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> MetricQuerySet:
        return MetricQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> MetricQuerySet:
        return self.get_queryset().get_all_names()

    def is_metric_available_for_topic(
        self, metric_name: str, topic_name: str
    ) -> MetricQuerySet:
        return self.get_queryset().is_metric_available_for_topic(
            metric_name=metric_name, topic_name=topic_name
        )
