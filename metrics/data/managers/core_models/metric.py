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
            QuerySet: A queryset of the individual metric names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_deaths_ONSByDay']>`

        """
        return self.all().values_list("name", flat=True).order_by("name")

    def is_metric_available_for_topic(self, metric_name: str, topic_name: str) -> bool:
        """Checks whether there are any metrics available for the given `metric_name` and `topic_name`

        Returns:
            bool: True if any `Metric` records match the criteria, False otherwise

        """
        return self.filter(name=metric_name, topic__name=topic_name).exists()

    def get_all_unique_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names without repetition
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_testing_PCRcountByDay']>`

        """
        return self.all().values_list("name", flat=True).distinct().order_by("name")

    def get_all_unique_change_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7daychange]>`
        """
        return self.get_all_unique_names().filter(name__contains="change")

    def get_all_unique_percent_change_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `percent`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7daypercentchange']>`

        """
        return self.get_all_unique_names().filter(name__icontains="percent")

    def get_all_headline_names(self) -> models.QuerySet:
        """Gets all unique headline metric names as a flat list queryset

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7daypercentchange']>`

        """
        return self.get_all_unique_names().filter(metric_group__name="headline")


class MetricManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> MetricQuerySet:
        return MetricQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> MetricQuerySet:
        """Gets all available metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_deaths_ONSByDay']>`

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

    def get_all_unique_names(self) -> MetricQuerySet:
        """Gets all unique metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names without repetition
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_testing_PCRcountByDay']>`

        """
        return self.get_queryset().get_all_unique_names()

    def get_all_unique_change_type_names(self) -> MetricQuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7daychange]>`

        """
        return self.get_queryset().get_all_unique_change_type_names()

    def get_all_unique_percent_change_type_names(self) -> MetricQuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `percent`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7daypercentchange']>`

        """
        return self.get_queryset().get_all_unique_percent_change_type_names()

    def get_all_headline_names(self) -> MetricQuerySet:
        """Gets all unique headline metric names as a flat list queryset

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7daypercentchange']>`

        """
        return self.get_queryset().get_all_headline_names()
