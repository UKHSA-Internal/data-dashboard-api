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
        return queryset.filter(age__name=age)

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
        queryset = self.filter(
            metric__topic__name=topic_name,
            metric__name=metric_name,
        )
        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            geography_code=geography_code,
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

    def query_for_data(
        self,
        *,
        topic_name: str,
        metric_name: str,
        fields_to_export: list[str],
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        geography_code: str = "",
        stratum_name: str = "",
        sex: str = "",
        age: str = "",
    ):
        """Filters for a N-item list of dicts by the given params if `fields_to_export` is used.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            fields_to_export: List of fields to be exported
                as part of the underlying `values()` call.
                If not specified, the full queryset is returned.
                Typically, this would be a 2 item list.
                In the case where we wanted to display
                the date along the x-axis and metric value across the y-axis:
                >>> ["date", "metric_value"]
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
           Queryset of (x_axis, y_axis) where x_axis represents the variable on the x_axis
           Eg: `85+` where age range is the headline variable of the chart and the y_axis
           is the metric value. A `latest_date` attribute is added to the queryset, which is
           take from the `period_end` of the selected headline metric.
           Examples:
               <CoreHeadlineQuerySet [{'age__name': '01-04', 'metric_value': Decimal('534.0000')}]>
        """
        queryset = self.get_queryset().get_headlines_released_from_embargo(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            age=age,
            sex=sex,
        )[:1]

        if fields_to_export:
            fields_to_export = [
                field for field in fields_to_export if field is not None
            ]
            queryset = queryset.values(*fields_to_export)

        queryset.latest_date = queryset.values_list("period_end", flat=True).first()

        return queryset

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
                E.g. `COVID-19_headline_7DayAdmissions`
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

    def query_for_superseded_data(
        self,
        *,
        topic_name: str,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        geography_code: str,
        stratum_name: str,
        sex: str,
        age: str,
    ) -> CoreHeadlineQuerySet:
        """Grabs all stale records which are not under embargo.

        Args:
           topic_name: The name of the threat being queried.
                E.g. `COVID-19`
           metric_name: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography_name: The name of the geography being queried.
               E.g. `England`
           geography_type_name: The name of the geography type being queried.
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
           The stale records in their entirety as a queryset

        """
        queryset = self.get_queryset().get_headlines_released_from_embargo(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            age=age,
            sex=sex,
        )
        # Note that we cannot slice / limit the above queryset.
        # This is because we will later call `delete()` on this queryset.
        # Which cannot be done since `OFFSET` and `DELETE` clauses are not allowed.
        # Since we always expect the number of resulting records to be fairly small.
        # We can pay the penalty of making the extra db call.
        try:
            live_headline_id: int = queryset.first().id
        except AttributeError:
            # Thrown when the queryset was empty
            # And `first()` returned `None`
            return queryset

        return queryset.exclude(id=live_headline_id)

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

    def delete_superseded_data(
        self,
        *,
        topic_name: str,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        geography_code: str,
        stratum_name: str,
        sex: str,
        age: str,
    ) -> None:
        """Deletes all stale records which are not under embargo.

        Args:
           topic_name: The name of the threat being queried.
                E.g. `COVID-19`
           metric_name: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography_name: The name of the geography being queried.
               E.g. `England`
           geography_type_name: The name of the geography type being queried.
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
           None

        """
        superseded_records = self.query_for_superseded_data(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            age=age,
            sex=sex,
        )
        superseded_records.delete()
