"""
This file contains the custom QuerySet and Manager classes associated with the `CoreHeadline` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

import datetime
from collections.abc import Iterable
from typing import Optional, Self

from django.db import models
from django.utils import timezone

from metrics.api.permissions.fluent_permissions import (
    validate_permissions_for_non_public,
)


class CoreHeadlineQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreHeadlineManager`"""

    @staticmethod
    def _newest_to_oldest(
        *, queryset: models.QuerySet, apply_refresh_date_only: bool
    ) -> models.QuerySet:
        if apply_refresh_date_only:
            return queryset.order_by("-refresh_date")
        return queryset.order_by("-period_end", "-refresh_date")

    @staticmethod
    def _filter_by_geography(
        *, queryset: models.QuerySet, geography: str
    ) -> models.QuerySet:
        return queryset.filter(geography__name=geography)

    @staticmethod
    def _filter_by_geography_type(
        *, queryset: models.QuerySet, geography_type: str
    ) -> models.QuerySet:
        return queryset.filter(geography__geography_type__name=geography_type)

    @staticmethod
    def _filter_by_geography_code(
        *, queryset: models.QuerySet, geography_code: str
    ) -> models.QuerySet:
        return queryset.filter(geography__geography_code=geography_code)

    @staticmethod
    def _filter_by_stratum(
        *, queryset: models.QuerySet, stratum: str
    ) -> models.QuerySet:
        return queryset.filter(stratum__name=stratum)

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
                queryset=queryset, geography=geography_name
            )

        if geography_type_name:
            queryset = self._filter_by_geography_type(
                queryset=queryset, geography_type=geography_type_name
            )

        if geography_code:
            queryset = self._filter_by_geography_code(
                queryset=queryset, geography_code=geography_code
            )

        if stratum_name:
            queryset = self._filter_by_stratum(queryset=queryset, stratum=stratum_name)

        if sex:
            queryset = self._filter_by_sex(queryset=queryset, sex=sex)

        if age:
            queryset = self._filter_by_age(queryset=queryset, age=age)

        return queryset

    def filter_headlines_for_audit_list(
        self,
        *,
        metric: str,
        geography: str,
        geography_type: str,
        stratum: str,
        sex: str,
        age: str,
    ) -> Self:
        """Filters for a given metric and includes records still under embargo for auditing.

        Args:
            metric: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography: The name of the geography being queried.
                E.g. `England`
            geography_type: The name of the geography
                type being queried.
                E.g. `Nation`
            stratum: The value of the stratum to apply additional filtering to.
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
            metric__name=metric,
        )
        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_type_name=geography_type,
            geography_name=geography,
            geography_code=None,
            stratum_name=stratum,
            age=age,
            sex=sex,
        )
        return self._newest_to_oldest(queryset=queryset, apply_refresh_date_only=False)

    def get_all_headlines_released_from_embargo(
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
        """Filters by the given parameters, inlcludes public and non-public data

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
        apply_refresh_date_only: bool = "alert" in topic_name
        return self._newest_to_oldest(
            queryset=queryset, apply_refresh_date_only=apply_refresh_date_only
        )

    def get_public_only_headlines_released_from_embargo(
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
        queryset = self.get_all_headlines_released_from_embargo(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
        )
        queryset = queryset.filter(is_public=True)
        apply_refresh_date_only: bool = "alert" in topic_name
        return self._newest_to_oldest(
            queryset=queryset, apply_refresh_date_only=apply_refresh_date_only
        )

    def get_non_public_only_headlines_released_from_embargo(
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
        queryset = self.get_all_headlines_released_from_embargo(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
        )
        queryset = queryset.filter(is_public=False)
        apply_refresh_date_only: bool = "alert" in topic_name
        return self._newest_to_oldest(
            queryset=queryset, apply_refresh_date_only=apply_refresh_date_only
        )

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

    def find_latest_released_embargo_for_metrics(
        self, *, metrics: set[str]
    ) -> datetime.datetime | None:
        """Finds the latest `embargo` timestamp which has been released for the associated `metrics`

        Args:
            metrics: Iterable of metric names
                to search the latest `embargo`
                timestamp against.

        Returns:
            A datetime object representing the latest
            embargo timestamp
            or None if no data could be found.

        """
        current_time = timezone.now()
        try:
            return (
                self.filter(metric__name__in=metrics, embargo__lte=current_time)
                .values_list("embargo", flat=True)
                .distinct()
                .latest("embargo")
            )
        except self.model.DoesNotExist:
            return None


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
        theme_name: str = "",
        sub_theme_name: str = "",
        rbac_permissions: Iterable["RBACPermission"] | None = None,
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
            theme_name: The name of the theme being queried.
                This is only used to determine permissions for
                the non-public portion of the requested dataset.
            sub_theme_name: The name of the sub theme being queried.
                This is only used to determine permissions for
                the non-public portion of the requested dataset.
            rbac_permissions: The RBAC permissions available
                to the given request. This dictates whether the given
                request is permitted access to non-public data or not.

        Returns:
           Queryset of (x_axis, y_axis) where x_axis represents the variable on the x_axis
           Eg: `85+` where age range is the headline variable of the chart and the y_axis
           is the metric value. A `latest_date` attribute is added to the queryset, which is
           taken from the `period_end` of the selected headline metric.
           Examples:
               <CoreHeadlineQuerySet [{'age__name': '01-04', 'metric_value': Decimal('534.0000')}]>
        """
        rbac_permissions = rbac_permissions or []
        has_access_to_non_public_data: bool = validate_permissions_for_non_public(
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            metric=metric_name,
            geography=geography_name,
            geography_type=geography_type_name,
            rbac_permissions=rbac_permissions,
        )

        if has_access_to_non_public_data:
            queryset = self.get_queryset().get_all_headlines_released_from_embargo(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_name=geography_name,
                geography_type_name=geography_type_name,
                geography_code=geography_code,
                stratum_name=stratum_name,
                age=age,
                sex=sex,
            )[:1]
        else:
            queryset = (
                self.get_queryset().get_public_only_headlines_released_from_embargo(
                    topic_name=topic_name,
                    metric_name=metric_name,
                    geography_name=geography_name,
                    geography_type_name=geography_type_name,
                    geography_code=geography_code,
                    stratum_name=stratum_name,
                    age=age,
                    sex=sex,
                )[:1]
            )

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
        theme_name: str = "",
        sub_theme_name: str = "",
        rbac_permissions: Iterable["RBACPermission"] | None = None,
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
            theme_name: The name of the theme being queried.
                This is only used to determine permissions for
                the non-public portion of the requested dataset.
            sub_theme_name: The name of the sub theme being queried.
                This is only used to determine permissions for
                the non-public portion of the requested dataset.
            rbac_permissions: The RBAC permissions available
                to the given request. This dictates whether the given
                request is permitted access to non-public data or not.

        Returns:
            The individual metric_value number and its associated `period_end` date
            Otherwise, None is returned if no record could be found
            Example:
                `(Decimal('6276.0000'), datetime.date(2023, 11, 1))`

        """
        rbac_permissions = rbac_permissions or []
        has_access_to_non_public_data: bool = validate_permissions_for_non_public(
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            metric=metric_name,
            geography=geography_name,
            geography_type=geography_type_name,
            rbac_permissions=rbac_permissions,
        )

        if has_access_to_non_public_data:
            queryset = self.get_queryset().get_all_headlines_released_from_embargo(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_name=geography_name,
                geography_type_name=geography_type_name,
                geography_code=geography_code,
                stratum_name=stratum_name,
                age=age,
                sex=sex,
            )
        else:
            queryset = (
                self.get_queryset().get_public_only_headlines_released_from_embargo(
                    topic_name=topic_name,
                    metric_name=metric_name,
                    geography_name=geography_name,
                    geography_type_name=geography_type_name,
                    geography_code=geography_code,
                    stratum_name=stratum_name,
                    age=age,
                    sex=sex,
                )
            )

        return queryset.first()

    def query_for_superseded_data(
        self,
        *,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str,
        stratum: str,
        sex: str,
        age: str,
        is_public: bool = True,
    ) -> CoreHeadlineQuerySet:
        """Grabs all stale records which are not under embargo.

        Args:
           topic: The name of the threat being queried.
                E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography: The name of the geography being queried.
               E.g. `England`
           geography_type: The name of the geography type being queried.
               E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum: The value of the stratum to apply additional filtering to.
               E.g. `default`, which would be used to capture all strata.
           sex: The gender to apply additional filtering to.
               E.g. `F`, would be used to capture Females.
               Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
               E.g. `0_4` would be used to capture the age of 0-4 years old
           is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Returns:
           The stale records in their entirety as a queryset

        """
        if is_public:
            queryset = (
                self.get_queryset().get_public_only_headlines_released_from_embargo(
                    topic_name=topic,
                    metric_name=metric,
                    geography_name=geography,
                    geography_type_name=geography_type,
                    stratum_name=stratum,
                    age=age,
                    sex=sex,
                )
            )
        else:
            queryset = (
                self.get_queryset().get_non_public_only_headlines_released_from_embargo(
                    topic_name=topic,
                    metric_name=metric,
                    geography_name=geography,
                    geography_type_name=geography_type,
                    stratum_name=stratum,
                    age=age,
                    sex=sex,
                )
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
        topic: str,
        metric: str,
        geography_codes: list[str],
        geography: str = "",
        geography_type: str = "",
        stratum: str = "",
        sex: str = "",
        age: str = "",
    ) -> dict[str, Optional["CoreHeadline"]]:
        """Grabs by the latest records by the given `topic` and `metric` with a current `period_end`

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography: The name of the geography being queried.
                E.g. `England`
            geography_type: The name of the geography
                type being queried.
                E.g. `Nation`
            geography_codes: Codes associated with the geographies being queried.
                E.g. ["E45000010", "E45000020"]
            stratum: The value of the stratum to apply additional filtering to.
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
                topic_name=topic,
                metric_name=metric,
                geography_name=geography,
                geography_type_name=geography_type,
                geography_code=geography_code,
                stratum_name=stratum,
                sex=sex,
                age=age,
            )
            for geography_code in geography_codes
        }

    def delete_superseded_data(
        self,
        *,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str,
        stratum: str,
        sex: str,
        age: str,
        is_public: bool = True,
    ) -> None:
        """Deletes all stale records which are not under embargo.

        Args:
           topic: The name of the threat being queried.
                E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography: The name of the geography being queried.
               E.g. `England`
           geography_type: The name of the geography type being queried.
               E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum: The value of the stratum to apply additional filtering to.
               E.g. `default`, which would be used to capture all strata.
           sex: The gender to apply additional filtering to.
               E.g. `F`, would be used to capture Females.
               Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
               E.g. `0_4` would be used to capture the age of 0-4 years old
           is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Returns:
           None

        """
        superseded_records = self.query_for_superseded_data(
            topic_name=topic,
            metric_name=metric,
            geography_name=geography,
            geography_type_name=geography_type,
            geography_code=geography_code,
            stratum_name=stratum,
            age=age,
            sex=sex,
            is_public=is_public,
        )
        superseded_records.delete()

    def find_latest_released_embargo_for_metrics(
        self, *, metrics: set[str]
    ) -> datetime.datetime | None:
        """Finds the latest `embargo` timestamp which has been released for the associated `metrics`

        Args:
            metrics: Iterable of metric names
                to search the latest `embargo`
                timestamp against.

        Returns:
            A datetime object representing the latest
            embargo timestamp
            or None if no data could be found.

        """
        return self.get_queryset().find_latest_released_embargo_for_metrics(
            metrics=metrics
        )
