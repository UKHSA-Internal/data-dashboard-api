"""
This file contains the custom QuerySet and Manager classes associated with the `CoreHeadline` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from decimal import Decimal

from django.db import models


class CoreHeadlineQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreHeadlineManager`"""

    @staticmethod
    def _newest_to_oldest(queryset: models.QuerySet) -> models.QuerySet:
        return queryset.order_by("-period_end")

    @staticmethod
    def _ascending_order(queryset: models.QuerySet, field_name: str) -> models.QuerySet:
        return queryset.order_by(field_name)

    def get_metric_value(self, topic_name: str, metric_name: str) -> "CoreHeadline":
        """Gets the record associated with the given `topic_name` and `metric_name`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_headline_ONSdeaths_7daytotals`

        Returns:
            QuerySet: A queryset containing the single record
                Examples:
                    `<CoreHeadline:
                        Core Headline Data for 2023-03-04,
                        metric 'COVID-19_headline_ONSdeaths_7daytotals',
                        value: 24298.0
                    >`

        Raises:
            `MultipleObjectsReturned`: If the query returned more than 1 record.
                We expect this if the provided `metric` is for timeseries type data

            `DoesNotExist`: If the query returned no records.

        """
        return self.get(
            metric__topic__name=topic_name,
            metric__name=metric_name,
        )

    def by_topic_metric_ordered_from_newest_to_oldest(
        self, topic_name: str, metric_name: str, geography_name: str
    ) -> models.QuerySet:
        """Filters by the given `topic_name` and `metric_name`. Slices all values older than the `date_from`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography being queried.
                E.g. `England`

        Returns:
            An ordered queryset from oldest -> newest
                of the individual metric_value numbers only:
                Examples:
                    `<CoreHeadlineQuerySet [ Decimal('2.0'), Decimal('9.0')]>`

        """
        queryset = self.filter(
            metric__metric_group__topic__name=topic_name,
            metric__name=metric_name,
            geography__name=geography_name,
        ).values_list("metric_value", flat=True)
        return self._newest_to_oldest(queryset=queryset)


class CoreHeadlineManager(models.Manager):
    """Custom model manager class for the `CoreHeadline` model."""

    def get_queryset(self) -> CoreHeadlineQuerySet:
        return CoreHeadlineQuerySet(model=self.model, using=self.db)

    def get_latest_metric_value(
        self, topic_name: str, metric_name: str, geography_name: str = "England",
    ) -> Decimal | None:
        """Grabs by the latest record by the given `topic_name` and `metric_name`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography being queried.
                E.g. `England`

        Returns:
            The individual metric_value number only.
            Otherwise, None is returned if no record could be found
            Examples:
                `2.0`

        """
        return (
            self.get_queryset()
            .by_topic_metric_ordered_from_newest_to_oldest(
                topic_name=topic_name, metric_name=metric_name, geography_name=geography_name
            )
            .first()
        )
