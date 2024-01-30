"""
This file contains the custom QuerySet and Manager classes associated with the `CoreTimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

import datetime

from django.db import models
from django.utils import timezone


class CoreTimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreTimeSeriesManager`"""

    @staticmethod
    def _ascending_order(queryset: models.QuerySet, field_name: str) -> models.QuerySet:
        return queryset.order_by(field_name)

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

    def filter_for_x_and_y_values(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        date_to: datetime.date | None = None,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ) -> models.QuerySet:
        """Filters for a 2-item object by the given params. Slices all values older than the `date_from`.

        Args:
            x_axis: The field to display along the x-axis.
                In this case, this will be the first item of each 2-item object
                E.g. `date` or `stratum`
            y_axis: The field to display along the y-axis
                In this case, this will be the second item of each 2-item object
                E.g. `metric`
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

        Notes:
            If `x_axis` and `y_axis` are not provided
            then the queryset will be returned for the
            full records instead of the 2-item values
            specified by the `x_axis` and `y_axis`

        Returns:
            QuerySet: An ordered queryset from lowest -> highest
                of the (x_axis, y_axis) numbers:
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
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        queryset = self.filter_for_latest_refresh_date_records(queryset=queryset)
        queryset = self._ascending_order(
            queryset=queryset,
            field_name=x_axis,
        )

        if x_axis and y_axis:
            queryset = queryset.values_list(x_axis, y_axis)

        return self._annotate_latest_date_on_queryset(queryset=queryset)

    @staticmethod
    def filter_for_latest_refresh_date_records(
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
        resulting_ids: list[int] = [
            record.id
            for record in queryset
            if record.refresh_date == latest_records_map.get(record.date)
        ]

        return queryset.filter(pk__in=resulting_ids)

    @staticmethod
    def _annotate_latest_date_on_queryset(
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
    def _exclude_data_under_embargo(queryset: models.QuerySet) -> models.QuerySet:
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

    def get_all_sex_names(self) -> models.QuerySet:
        """Gets all available sex names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sex names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<CoreTimeSeriesQuerySet ['ALL', 'F', 'M']>`

        """
        return self.values_list("sex", flat=True).distinct()


class CoreTimeSeriesManager(models.Manager):
    """Custom model manager class for the `TimeSeries` model."""

    def get_queryset(self) -> CoreTimeSeriesQuerySet:
        return CoreTimeSeriesQuerySet(model=self.model, using=self.db)

    def filter_for_x_and_y_values(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        date_to: datetime.date | None = None,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ) -> CoreTimeSeriesQuerySet:
        """Filters for a 2-item object by the given params. Slices all values older than the `date_from`.

        Args:
            x_axis: The field to display along the x-axis.
                In this case, this will be the first item of each 2-item object
                E.g. `date` or `stratum`
            y_axis: The field to display along the y-axis
                In this case, this will be the second item of each 2-item object
                E.g. `metric`
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
        return self.get_queryset().filter_for_x_and_y_values(
            x_axis=x_axis,
            y_axis=y_axis,
            topic_name=topic_name,
            metric_name=metric_name,
            date_from=date_from,
            date_to=date_to,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
        )

    def get_all_sex_names(self) -> models.QuerySet:
        """Gets all available sex names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sex names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<CoreTimeSeriesQuerySet [('ALL'), ('F'), ('M')]>`

        """
        return self.get_queryset().get_all_sex_names()
