"""
This file contains the custom QuerySet and Manager classes associated with the `Metric` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models


class MetricQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `MetricManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names:
                Examples:
                    `<MetricQuerySet ['new_cases_daily', 'new_deaths_daily']>`

        """
        return self.all().values_list("name", flat=True)

    def is_metric_available_for_topic(self, metric_name: str, topic_name: str) -> bool:
        """Checks whether there are any metrics available for the given `metric_name` and `topic_name`

        Returns:
            bool: True if any `Metric` records match the criteria, False otherwise

        """
        return self.filter(name=metric_name, topic__name=topic_name).exists()

    def get_all_unique_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_daily', 'new_deaths_daily']>`

        """
        return self.all().values_list("name", flat=True).distinct()

    def get_all_unique_change_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change', 'new_deaths_7days_change']>`

        """
        return self.get_all_unique_names().filter(name__contains="change")

    def get_all_unique_percent_change_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the words `change` and `percent`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change_percentage', 'weekly_percent_change_positivity']>`

        """
        return self.get_all_unique_names().filter(name__contains="change")


class MetricManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> MetricQuerySet:
        return MetricQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> MetricQuerySet:
        """Gets all available metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names:
                Examples:
                    `<MetricQuerySet ['new_cases_daily', 'new_deaths_daily']>`

        """
        return self.get_queryset().get_all_names()

    def is_metric_available_for_topic(self, metric_name: str, topic_name: str) -> bool:
        """Checks whether there are any metrics available for the given `metric_name` and `topic_name`

        Returns:
            bool: True if any `Metric` records match the criteria, False otherwise

        """
        return self.get_queryset().is_metric_available_for_topic(
            metric_name=metric_name, topic_name=topic_name
        )

    def get_all_unique_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_daily', 'new_deaths_daily']>`

        """
        return self.get_queryset().get_all_unique_names()

    def get_all_unique_change_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change', 'new_deaths_7days_change']>`

        """
        return self.get_queryset().get_all_unique_change_type_names()

    def get_all_unique_change_percent_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change_percentage', 'new_deaths_7days_change_percentage']>`

        """
        return self.get_queryset().get_all_unique_change_type_names()
