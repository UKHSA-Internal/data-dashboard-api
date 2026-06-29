"""
This file contains the custom QuerySet and Manager classes associated with the `Metric` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class MetricQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `MetricManager`"""

    def get_name_by_id(self, metric_id: int) -> str | None:
        """
        Gets the metric name which matches the given theme id.

        Args:
            metric_id: The ID of the metric to look up

        Returns:
            The metric name if found, None otherwise

        Examples:
            >>> MetricQuerySet.get_name_by_id(1)
            'infectious_disease'
            >>> MetricQuerySet.get_name_by_id(999)
            None
        """
        return self.filter(id=metric_id).values_list("name", flat=True).first()

    def get_id_by_name(self, metric_name: str) -> int | None:
        """
        Gets the metric ID for a given metric name.

        Returns:
            The metric ID if found, or None otherwise
        """
        record = self.filter(name=metric_name).first()
        return int(record.id) if record else None

    def get_all_names(self) -> models.QuerySet:
        """Gets all available metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_deaths_ONSByDay']>`

        """
        return self.all().values_list("name", flat=True).order_by("name")

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
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7DayChange']>`
        """
        return self.get_all_unique_names().filter(
            models.Q(name__icontains="change") & ~models.Q(name__icontains="percent")
        )

    def get_all_unique_percent_change_type_names(self) -> models.QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `percent`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7DayPercentChange']>`

        """
        return self.get_all_unique_names().filter(name__icontains="percent")

    def get_all_timeseries_names(self) -> models.QuerySet:
        """Gets all unique metric names that have a `timeseries` metric_group
            and returns them as a flat list.

        Returns:
            QuerySet: A queryset of the individual metric names without repetition
                ordered in descending ordering starting from A -> Z:
                    Examples:
                        `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_testing_PCRcountByDay']>`

        """
        return self.get_all_unique_names().exclude(metric_group__name="headline")

    def get_all_headline_names(self) -> models.QuerySet:
        """Gets all unique headline metric names as a flat list queryset

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7DayPercentChange']>`

        """
        return self.get_all_unique_names().filter(metric_group__name="headline")

    def get_filtered_unique_names_related_to_parent_topic_id(
        self, parent_topic_id
    ) -> models.QuerySet:
        """Gets all available unique metrics with id and name fields that are related to the parent topic ID.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': '6-in-1_coverage_coverageByYear'}, {'id': 2, 'name': 'MMR1_coverage_coverageByYear'}, ...]>`
        """
        return self.filter(topic_id=parent_topic_id).values("id", "name").distinct()

    def get_all_names_and_ids(self) -> models.QuerySet:
        """Gets all available metrics with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': '6-in-1_coverage_coverageByYear'}, {'id': 2, 'name': 'MMR1_coverage_coverageByYear'}, ...]>`
        """
        return self.all().values("id", "name").distinct()


class MetricManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> MetricQuerySet:
        return MetricQuerySet(model=self.model, using=self.db)

    def get_name_by_id(self, metric_id: int) -> str | None:
        """Gets the metric name which matches the given metric id.

        Args:
            metric_id: The ID of the theme to look up

        Returns:
            The metric name if found, None otherwise

        Examples:
            >>> MetricManager.get_name_by_id(1)
            'COVID-19'
            >>> MetricManager.get_name_by_id(999)
            None
        """
        return self.get_queryset().get_name_by_id(metric_id)

    def get_id_by_name(self, metric_name: str) -> int | None:
        """
        Gets the metric ID for a given metric name.

        Returns:
            The metric ID if found, or None otherwise
        """
        return self.get_queryset().get_id_by_name(metric_name)

    def get_all_names(self) -> MetricQuerySet:
        """Gets all available metric names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual metric names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_deaths_ONSByDay']>`

        """
        return self.get_queryset().get_all_names()

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
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7DayChange']>`

        """
        return self.get_queryset().get_all_unique_change_type_names()

    def get_all_unique_percent_change_type_names(self) -> MetricQuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `percent`

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7DayPercentChange']>`

        """
        return self.get_queryset().get_all_unique_percent_change_type_names()

    def get_all_timeseries_names(self) -> MetricQuerySet:
        """Gets all unique timeseries metric names as a flat list queryset

        Returns:
            QuerySet: A queryset of the individual metric names without repetition
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_testing_PCRcountByDay']>`
        """
        return self.get_queryset().get_all_timeseries_names()

    def get_all_headline_names(self) -> MetricQuerySet:
        """Gets all unique headline metric names as a flat list queryset

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_ONSdeaths_7DayPercentChange']>`

        """
        return self.get_queryset().get_all_headline_names()

    def get_filtered_unique_names_related_to_parent_topic_id(
        self, parent_topic_id: str
    ) -> MetricQuerySet:
        """Gets all available metrics with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<MetricQuerySet [{'id': 1, 'name': '6-in-1_coverage_coverageByYear'}, {'id': 2, 'name': 'MMR1_coverage_coverageByYear'}, ...]>`
        """
        return self.get_queryset().get_filtered_unique_names_related_to_parent_topic_id(
            parent_topic_id=parent_topic_id
        )

    def get_all_names_and_ids(self) -> MetricQuerySet:
        """Gets all available metrics with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<MetricQuerySet [{'id': 1, 'name': '6-in-1_coverage_coverageByYear'}, {'id': 2, 'name': 'MMR1_coverage_coverageByYear'}, ...]>`
        """
        return self.get_queryset().get_all_names_and_ids()
