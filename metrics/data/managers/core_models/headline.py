"""
This file contains the custom QuerySet and Manager classes associated with the `CoreHeadline` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from typing import Optional, Self

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
    def _filter_by_geography_code(
        *, queryset: models.QuerySet, geography_code: str
    ) -> models.QuerySet:
        return queryset.filter(geography__geography_code=geography_code)

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
        result = queryset.filter(age__name=age)
        #breakpoint()
        return result
        # return queryset.filter(age__name=age)

    def _filter_for_any_optional_fields(
        self,
        *,
        queryset: Self,
        geography_name: str,
        geography_type_name: str,
        geography_code: str,
        stratum_name: str,
        sex: str,
        age: str,
    ) -> Self:
        if geography_name:
            queryset = self._filter_by_geography(
                queryset=queryset, geography_name=geography_name
            )

        if geography_type_name:
            queryset = self._filter_by_geography_type(
                queryset=queryset, geography_type_name=geography_type_name
            )

        if geography_code:
            queryset = self._filter_by_geography_code(
                queryset=queryset, geography_code=geography_code
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
        geography_code: str = "",
    ) -> Self:
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
            geography_code: The code associated with the geography being queried.
                E.g. `E92000001`
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
        #breakpoint()
        queryset = self.filter(
            metric__topic__name=topic_name,
            metric__name=metric_name,
        )
        # were getting data to this point.
        #breakpoint()
        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            age=age,
            sex=sex,
        )
        #breakpoint()
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        return self._newest_to_oldest(queryset=queryset)

    @staticmethod
    def _exclude_data_under_embargo(*, queryset: models.QuerySet) -> models.QuerySet:
        """Excludes any data which is currently embargoed from the given `queryset`

        Notes:
            If the `embargo` value is None then it will be included
            in the returned queryset

        Args:
            queryset: The queryset to exclude embargoed data from

        Returns:
            The filtered queryset which excludes embargoed data

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
        geography_code: str = "",
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
            geography_code: Code associated with the geography being queried.
                E.g. "E45000010"
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
                geography_code=geography_code,
                stratum_name=stratum_name,
                age=age,
                sex=sex,
            )
            .first()
        )

    def filter_for_x_and_y_values(
        self,
        *,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: "",
        date_to: "",
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ) -> models.QuerySet:
        """Filters for a 2-item object by the given params.

        Notes:
            What should happen if the x and y axis aren't provided.

        Returns
            Queryset: of the (x_axis, y_axis) numbers
            variable group, eg: age 85+ and metric_value as decimal
        """
        queryset = (
            self.get_queryset()
            .get_headlines_released_from_embargo(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_name=geography_name,
                geography_type_name=geography_type_name,
                geography_code="",
                stratum_name=stratum_name,
                age=age,
                sex=sex,
            )
        )

        if x_axis and y_axis:
            queryset = queryset.values_list(x_axis, y_axis)

        return queryset

    def get_latest_headlines_for_geography_codes(
        self,
        *,
        topic_name: str,
        metric_name: str,
        geography_codes: list[str],
        geography_name: str = "",
        geography_type_name: str = "",
        stratum_name: str = "",
        sex: str = "",
        age: str = "",
    ) -> dict[str, Optional["CoreHeadline"]]:
        """Grabs by the latest records by the given `topic_name` and `metric_name` with a current `period_end`

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
            geography_codes: Codes associated with the geographies being queried.
                E.g. ["E45000010", "E45000020"]
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old

        Returns:
            Dict keyed by each geography code,
            with the value being the individual `CoreHeadline` record
            which has been lifted from embargo
            and has a `period_end` which is currently valid.
            Otherwise, the value will be None

        """
        return {
            geography_code: self.get_latest_headline(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_name=geography_name,
                geography_type_name=geography_type_name,
                geography_code=geography_code,
                stratum_name=stratum_name,
                sex=sex,
                age=age,
            )
            for geography_code in geography_codes
        }
