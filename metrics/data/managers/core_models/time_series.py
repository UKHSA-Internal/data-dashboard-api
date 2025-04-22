"""
This file contains the custom QuerySet and Manager classes associated with the `CoreTimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

import datetime
from collections.abc import Iterable
from typing import Self

from django.db import models
from django.utils import timezone

from metrics.api.permissions.fluent_permissions import validate_permissions
from metrics.data.models import RBACPermission


class CoreTimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreTimeSeriesManager`"""

    @staticmethod
    def _ascending_order(
        *, queryset: models.QuerySet, field_name: str
    ) -> models.QuerySet:
        return queryset.order_by(field_name)

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

    def filter_for_audit_list_view(
        self,
        *,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        stratum_name: str,
        sex: str,
        age: str,
    ) -> models.QuerySet:
        """Filters for all records based on the provided arguments including `metric`, `geography_name` etc.
            returns all records including those under `embargo` or `stale/duplicated` records.

        Args:
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old

        Returns:
            QuerySet: A date ordered queryset from oldest -> newest
            Example:
                `<CoreTimeSeriesQuerySet [
                    (datetime.date(2022, 10, 10), Decimal('0.8')),
                    (datetime.date(2022, 10, 17), Decimal('0.9'))
                ]>`

        """
        queryset = self.filter(
            metric__name=metric_name,
        )

        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
        )

        return self._ascending_order(queryset=queryset, field_name="date")

    def query_for_data(
        self,
        *,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        date_to: datetime.date | None = None,
        fields_to_export: list[str] = None,
        field_to_order_by: str = "date",
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
        restrict_to_public: bool = True,
    ) -> models.QuerySet:
        """Filters for a N-item list of dicts by the given params if `fields_to_export` is used.

        Notes:
            - Slices all values older than the `date_from` and all values newer than the `date_to`.
            - If `fields_to_export` is not specified, then the full queryset is returned

        Args:
            fields_to_export: List of fields to be exported
                as part of the underlying `values()` call.
                If not specified, the full queryset is returned.
                Typically, this would be a 2 item list.
                In the case where we wanted to display
                the date along the x-axis and metric value across the y-axis:
                >>> ["date", "metric_value"]
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
            date_to: The datetime object to end the query at.
                E.g. datetime.datetime(2023, 5, 27, 0, 0, 0, 0)
                would cut off any records that occurred after that date.
            field_to_order_by: The name of the field to order
                the resulting queryset in ascending order by.
                Defaults to `date`.
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old
            restrict_to_public: Boolean switch to restrict the query
                to only return public records.
                If False, then non-public records will be included.

        Returns:
            QuerySet: An ordered queryset from lowest -> highest
                of the (fields_to_export) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        queryset = self.filter(
            metric__topic__name=topic_name,
            metric__name=metric_name,
            date__gte=date_from,
            date__lte=date_to,
        )
        queryset = self._filter_for_any_optional_fields(
            queryset=queryset,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
        )
        if restrict_to_public:
            queryset = queryset.filter(is_public=True)

        queryset = self._exclude_data_under_embargo(queryset=queryset)
        queryset = self.filter_for_latest_refresh_date_records(queryset=queryset)
        queryset = self._ascending_order(
            queryset=queryset,
            field_name=field_to_order_by,
        )

        if fields_to_export:
            fields_to_export = [
                field for field in fields_to_export if field is not None
            ]
            queryset = queryset.values(*fields_to_export)

        return self._annotate_latest_date_on_queryset(queryset=queryset)

    def query_for_superseded_data(
        self,
        *,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        geography_code: str,
        stratum_name: str,
        sex: str,
        age: str,
        is_public: bool,
    ) -> Self:
        """Grabs all stale records which are not under embargo.

        Args:
           metric_name: The name of the metric being queried.
               E.g. `COVID-COVID-19_cases_countRollingMean`
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
          is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Returns:
           The stale records in their entirety as a queryset

        """
        queryset = self.filter(
            metric__name=metric_name,
            geography__name=geography_name,
            geography__geography_code=geography_code,
            geography__geography_type__name=geography_type_name,
            stratum__name=stratum_name,
            age__name=age,
            sex=sex,
            is_public=is_public,
        )
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        return self.filter_for_outdated_refresh_date_records(queryset=queryset)

    def filter_for_outdated_refresh_date_records(self, *, queryset: Self) -> Self:
        """Filters the given `queryset` for the stale records in each individual date

        Notes:
            If we have the following input `queryset`:
                ----------------------------------------
                | 2023-01-01 | 2023-01-02 | 2023-01-03 |
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- entirely superseded
                | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded with a final successor
                |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
                | 4th round  |      -     |     -      |   <- 'head' round with no successors
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- expected results
                | 2nd round  |      -     | 2nd round  |

        Args:
            queryset: The queryset to filter against

        Returns:
            A new filtered queryset containing
            only the stale records for each date

        """
        latest_record_ids: list[int] = self._get_ids_of_latest_records(
            queryset=queryset
        )
        return queryset.exclude(pk__in=latest_record_ids)

    def filter_for_latest_refresh_date_records(
        self,
        *,
        queryset: models.QuerySet,
    ) -> models.QuerySet:
        """Filters the given `queryset` to ensure the latest record is returned for each individual date

        Notes:
            If we have the following input `queryset`:
                ----------------------------------------
                | 2023-01-01 | 2023-01-02 | 2023-01-03 |
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- entirely superseded
                | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded with a final successor
                |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
                | 4th round  |      -     |     -      |   <- 'head' round with no successors
                ----------------------------------------
                | 4th round  | 2nd round  | 3rd round  |   <- expected results

            This method will handle mixtures of records
            so that we don't simply return the latest round
            in its entirety but rather the overall result
            which return the most recent record
            for the individual dates

        Args:
            queryset: The queryset to filter against

        Returns:
            A new filtered queryset containing
            only the latest records for each date

        """
        latest_record_ids: list[int] = self._get_ids_of_latest_records(
            queryset=queryset
        )
        return queryset.filter(pk__in=latest_record_ids)

    @classmethod
    def _get_ids_of_latest_records(cls, queryset: Self) -> list[int]:
        # Build a queryset labelled with the latest `refresh_date` for each `date`
        latest_refresh_dates_associated_with_dates: CoreTimeSeriesQuerySet = (
            queryset.values("date").annotate(latest_refresh=models.Max("refresh_date"))
        )

        # Store the latest records for each day so that they can be mapped easily
        # Note that this currently incurs execution of an additional db query
        # The alternative was to possibly use `DISTINCT ON` instead
        # but that is specific to the postgresql backend and would
        # mean we would no longer be agnostic to the underlying database engine.
        # Given the level of caching in the system, the performance penalty incurred
        # here is not noticeable.
        latest_records_map: dict[datetime.date, datetime.date] = {
            record["date"]: record["latest_refresh"]
            for record in latest_refresh_dates_associated_with_dates
        }

        # Filter the IDs for the records in memory to get the latest ones partitioned by each date
        return [
            record.id
            for record in queryset
            if record.refresh_date == latest_records_map.get(record.date)
        ]

    @staticmethod
    def _annotate_latest_date_on_queryset(
        *,
        queryset: models.QuerySet,
    ) -> models.QuerySet:
        """Sets `latest_date` attribute on the given `queryset`

        Notes:
            The `latest_date` attribute is set according to
            the latest/maximum date associated with any of the records
            returned within the given `queryset`.
            This is a custom attribute, so this must be the final queryset operation.
            If additional filtering is performed, then this attribute will be lost

        Args:
            queryset: The queryset to be labelled with
                the `latest_date` attribute

        Returns:
            The queryset which has been labelled with
            the `latest_date` attribute

        """
        latest_date_aggregation = queryset.aggregate(latest_date=models.Max("date"))
        queryset.latest_date = latest_date_aggregation["latest_date"]
        return queryset

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

    def get_available_geographies(self, *, topic: str) -> models.QuerySet:
        """Gets all available geographies for the given `topic` which have at least 1 `CoreTimeSeries` record

        Returns:
            QuerySet: A queryset of the geography types and the corresponding geographies
                Examples:
                    `<CoreTimeSeriesQuerySet
                        [Row(geography__name='England', geography__geography_type__name='Nation')]>`

        """
        return (
            self.filter(metric__topic__name=topic)
            .values_list(
                "geography__name", "geography__geography_type__name", named=True
            )
            .order_by("geography__geography_type__name", "geography__name")
            .distinct()
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


class CoreTimeSeriesManager(models.Manager):
    """Custom model manager class for the `TimeSeries` model."""

    def query_for_data(
        self,
        *,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        fields_to_export: list[str] | None = None,
        date_to: datetime.date | None = None,
        field_to_order_by: str = "date",
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
        rbac_permissions: Iterable[RBACPermission] | None = None,
    ) -> CoreTimeSeriesQuerySet:
        """Filters for a 2-item object by the given params. Slices all values older than the `date_from`.

        Args:
            fields_to_export: List of fields to be exported
                as part of the underlying `values()` call.
                If not specified, the full queryset is returned.
                Typically, this would be a 2 item list.
                In the case where we wanted to display
                the date along the x-axis and metric value across the y-axis:
                >>> ["date", "metric_value"]
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
            date_to: The datetime object to end the query at.
                E.g. datetime.datetime(2023, 5, 27, 0, 0, 0, 0)
                would cut off any records that occurred after that date.
            field_to_order_by: The name of the field to order
                the resulting queryset in ascending order by.
                Defaults to `date`.
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `0_4`, which would be used to capture the age group 0 to 4 years old.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old
            rbac_permissions: The RBAC permissions available
                to the given request. This dictates whether the given
                request is permitted access to non-public data or not.

        Notes:
            If we have the following input `queryset`:
                ----------------------------------------
                | 2023-01-01 | 2023-01-02 | 2023-01-03 |
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- entirely superseded
                | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded with a final successor
                |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
                | 4th round  |      -     |     -      |   <- 'head' round with no successors
                ----------------------------------------
                | 4th round  | 2nd round  | 3rd round  |   <- expected results

            This method will handle mixtures of records
            so that we don't simply return the latest round
            in its entirety but rather the overall result
            which return the most recent record
            for the individual dates

        Returns:
            QuerySet: An ordered queryset from lowest -> highest
                of the (x_axis, y_axis) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('8.0')),
                        (datetime.date(2022, 10, 17), Decimal('9.0'))
                    ]>`

        """
        rbac_permissions: Iterable[RBACPermission] = rbac_permissions or []
        has_access_to_non_public_data: bool = validate_permissions(
            theme="",
            sub_theme="",
            topic=topic_name,
            metric=metric_name,
            geography_type=geography_type_name,
            geography=geography_name,
            rbac_permissions=rbac_permissions,
        )

        return self.get_queryset().query_for_data(
            fields_to_export=fields_to_export,
            field_to_order_by=field_to_order_by,
            topic_name=topic_name,
            metric_name=metric_name,
            date_from=date_from,
            date_to=date_to,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
            restrict_to_public=not has_access_to_non_public_data,
        )

    def query_for_superseded_data(
        self,
        *,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        geography_code: str,
        stratum_name: str,
        sex: str,
        age: str,
        is_public: bool,
    ) -> CoreTimeSeriesQuerySet:
        """Filters the given `queryset` for the stale records in each individual date

        Args:
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `0_4`, which would be used to capture the age group 0 to 4 years old.
           sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old
           is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Notes:
            If we have the following input `queryset`:
                ----------------------------------------
                | 2023-01-01 | 2023-01-02 | 2023-01-03 |
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- entirely superseded
                | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded with a final successor
                |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
                | 4th round  |      -     |     -      |   <- 'head' round with no successors
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- expected results
                | 2nd round  |      -     | 2nd round  |

        Returns:
            A new filtered queryset containing
            only the stale records for each date

        """
        return self.get_queryset().query_for_superseded_data(
            metric_name=metric_name,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
            is_public=is_public,
        )

    def get_queryset(self) -> CoreTimeSeriesQuerySet:
        return CoreTimeSeriesQuerySet(model=self.model, using=self.db)

    def get_available_geographies(self, *, topic: str) -> models.QuerySet:
        """Gets all available geographies for the given `topic` which have at least 1 `CoreTimeSeries` record

        Returns:
            QuerySet: A queryset of the geography types and the corresponding geographies
                Examples:
                    `<CoreTimeSeriesQuerySet
                        [Row(geography__name='England', geography__geography_type__name='Nation')]>`

        """
        return self.get_queryset().get_available_geographies(topic=topic)

    def delete_superseded_data(
        self,
        *,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        geography_code: str,
        stratum_name: str,
        sex: str,
        age: str,
        is_public: bool,
    ) -> None:
        """Deletes all stale records within each individual date

        Args:
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `0_4`, which would be used to capture the age group 0 to 4 years old.
           sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old
           is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Notes:
            If we have the following input `queryset`:
                ----------------------------------------
                | 2023-01-01 | 2023-01-02 | 2023-01-03 |
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- entirely superseded
                | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded with a final successor
                |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
                | 4th round  |      -     |     -      |   <- 'head' round with no successors
                ----------------------------------------
                | 1st round  | 1st round  | 1st round  |   <- expected results
                | 2nd round  |      -     | 2nd round  |

        Returns:
            None

        """
        superseded_records = self.query_for_superseded_data(
            metric_name=metric_name,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            geography_code=geography_code,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
            is_public=is_public,
        )
        superseded_records.delete()

    def find_latest_released_embargo_for_metrics(
        self, metrics: set[str]
    ) -> datetime.datetime:
        """Finds the latest `embargo` timestamp which has been released for the associated `metrics`

        Args:
            metrics: Iterable of metric names
                to search the latest `embargo`
                timestamp against.

        Returns:
            A datetime object representing the latest
            embargo timestamp.

        """
        return self.get_queryset().find_latest_released_embargo_for_metrics(
            metrics=metrics
        )
