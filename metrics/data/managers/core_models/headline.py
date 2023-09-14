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
                E.g. `COVID-19_headline_ONSdeaths_7DayTotals`

        Returns:
            QuerySet: A queryset containing the single record
                Examples:
                    `<CoreHeadline:
                        Core Headline Data for 2023-03-04,
                        metric 'COVID-19_headline_ONSdeaths_7DayTotals',
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

    @staticmethod
    def _filter_by_geography(queryset, geography_name):
        return queryset.filter(geography__name=geography_name)

    @staticmethod
    def _filter_by_geography_type(queryset, geography_type_name):
        return queryset.filter(geography__geography_type__name=geography_type_name)

    @staticmethod
    def _filter_by_stratum(queryset, stratum_name):
        return queryset.filter(stratum__name=stratum_name)

    @staticmethod
    def _filter_by_sex(queryset, sex):
        return queryset.filter(sex=sex)

    @staticmethod
    def _filter_by_age(queryset, age):
        return queryset.filter(age__name=age)

    def _filter_for_any_optional_fields(
        self,
        queryset,
        geography_name,
        geography_type_name,
        stratum_name,
        sex,
        age,
    ):
        if geography_name:
            queryset = self._filter_by_geography(
                queryset=queryset, geography_name=geography_name
            )

        if geography_type_name:
            queryset = self._filter_by_geography_type(
                queryset=queryset, geography_type_name=geography_type_name
            )

        if stratum_name:
            queryset = self._filter_by_stratum(
                queryset=queryset, stratum_name=stratum_name
            )

        if sex:
            queryset = self._filter_by_sex(queryset=queryset, sex=sex)

        if age:
            queryset = self._filter_by_age(queryset=queryset, age=age)

        return queryset

    def by_topic_metric_ordered_from_newest_to_oldest(
        self,
        topic_name: str,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        stratum_name: str,
        sex: str,
        age: str,
    ) -> models.QuerySet:
        """Filters by the given `topic_name` and `metric_name`

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography being queried.
                E.g. `England`
            geography_type_name: The name of the geography
                type being queried.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old

        Returns:
            An ordered queryset from oldest -> newest
                of the individual metric_value numbers only:
                Examples:
                    `<CoreHeadlineQuerySet [ Decimal('2.0'), Decimal('9.0')]>`

        """
        queryset = self.filter(
            metric__metric_group__topic__name=topic_name,
            metric__name=metric_name,
        ).values_list("metric_value", flat=True)

        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            stratum_name=stratum_name,
            age=age,
            sex=sex,
        )

        return self._newest_to_oldest(queryset=queryset)


class CoreHeadlineManager(models.Manager):
    """Custom model manager class for the `CoreHeadline` model."""

    def get_queryset(self) -> CoreHeadlineQuerySet:
        return CoreHeadlineQuerySet(model=self.model, using=self.db)

    def get_latest_metric_value(
        self,
        topic_name: str,
        metric_name: str,
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        stratum_name: str = "",
        sex: str = "",
        age: str = "",
    ) -> Decimal | None:
        """Grabs by the latest record by the given `topic_name` and `metric_name`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography being queried.
                E.g. `England`
            geography_type_name: The name of the geography
                type being queried.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old


        Returns:
            The individual metric_value number only.
            Otherwise, None is returned if no record could be found
            Examples:
                `2.0`

        """
        return (
            self.get_queryset()
            .by_topic_metric_ordered_from_newest_to_oldest(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_name=geography_name,
                geography_type_name=geography_type_name,
                stratum_name=stratum_name,
                age=age,
                sex=sex,
            )
            .first()
        )
