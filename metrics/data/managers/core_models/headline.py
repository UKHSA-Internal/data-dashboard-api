"""
This file contains the custom QuerySet and Manager classes associated with the `CoreHeadline` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models
from django.utils import timezone


class CoreHeadlineQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreHeadlineManager`"""

    @staticmethod
    def _newest_to_oldest(*, queryset: models.QuerySet) -> models.QuerySet:
        return queryset.order_by("-period_end", "-refresh_date")

    @staticmethod
    def _filter_by_geography(
        *, queryset: models.QuerySet, geography_name: str
    ) -> models.QuerySet:
        return queryset.filter(geography__name=geography_name)

    @staticmethod
    def _filter_by_geography_type(
        *, queryset: models.QuerySet, geography_type_name: str
    ) -> models.QuerySet:
        return queryset.filter(geography__geography_type__name=geography_type_name)

    @staticmethod
    def _filter_by_stratum(
        *, queryset: models.QuerySet, stratum_name: str
    ) -> models.QuerySet:
        return queryset.filter(stratum__name=stratum_name)

    @staticmethod
    def _filter_by_sex(*, queryset: models.QuerySet, sex: str) -> models.QuerySet:
        return queryset.filter(sex=sex)

    @staticmethod
    def _filter_by_age(*, queryset: models.QuerySet, age: str) -> models.QuerySet:
        return queryset.filter(age__name=age)

    def _filter_for_any_optional_fields(
        self,
        *,
        queryset: models.QuerySet,
        geography_name: str,
        geography_type_name: str,
        stratum_name: str,
        sex: str,
        age: str,
    ) -> models.QuerySet:
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

    def get_headlines_released_from_embargo(
        self,
        *,
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
            An ordered queryset from oldest -> newest:
                Examples:
                    `<CoreHeadlineQuerySet [
                        <CoreHeadline: Core Headline Data for 2023-09-30 23:00:00+00:00,
                         metric 'COVID-19_headline_positivity_latest',
                         value: 99.0000>
                        ]>`

        """
        queryset = self.filter(
            metric__topic__name=topic_name,
            metric__name=metric_name,
        )
        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            stratum_name=stratum_name,
            age=age,
            sex=sex,
        )
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        return self._newest_to_oldest(queryset=queryset)

    @staticmethod
    def _exclude_data_under_embargo(*, queryset: models.QuerySet) -> models.QuerySet:
        """Excludes any data which is currently embargoed from the given `queryset`

        Notes:
            If the `embargo` value is None then it will be included
            in the returned queryset

        Args:
            queryset: The queryset to exclude emargoed data from

        Returns:
            The filtered queryset which excludes emargoed data

        """
        current_time = timezone.now()
        return queryset.filter(
            models.Q(embargo__lte=current_time) | models.Q(embargo=None)
        )


class CoreHeadlineManager(models.Manager):
    """Custom model manager class for the `CoreHeadline` model."""

    def get_queryset(self) -> CoreHeadlineQuerySet:
        return CoreHeadlineQuerySet(model=self.model, using=self.db)

    def get_latest_headline(
        self,
        *,
        topic_name: str,
        metric_name: str,
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        stratum_name: str = "",
        sex: str = "",
        age: str = "",
    ) -> "CoreHeadline":
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
            The individual metric_value number and its associated `period_end` date
            Otherwise, None is returned if no record could be found
            Example:
                `(Decimal('6276.0000'), datetime.date(2023, 11, 1))`

        """
        return (
            self.get_queryset()
            .get_headlines_released_from_embargo(
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
