"""
This file contains the custom QuerySet and Manager classes associated with the `APITimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
import datetime

from django.db import models
from django.utils import timezone


class APITimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `APITimeSeriesManager`"""

    def get_distinct_column_values_with_filters(
        self, lookup_field: str, **kwargs
    ) -> "APITimeSeriesQuerySet":
        """Filters for unique values in the column denoted by `lookup_field` via the given **kwargs.

        Args:
            lookup_field: A column to query and retrieve unique values for.
            **kwargs: The filters to apply to the query.

        Returns:
            APITimeSeriesQuerySet: The unique column values as a queryset.
            Examples:
                `<APITimeSeriesQuerySet ['infectious_disease']>`

        """
        return self.filter(**kwargs).values_list(lookup_field, flat=True).distinct()

    def filter_for_list_view(
        self,
        theme_name: str,
        sub_theme_name: str,
        topic_name: str,
        geography_type_name: str,
        geography_name: str,
        metric_name: str,
    ) -> "APITimeSeriesQuerySet":
        """Filters by the given fields to provide a slice of the timeseries data as per the fields.

        Args:
            theme_name: The name of the root theme being queried for.
                E.g. `infectious_disease`
            sub_theme_name: The name of the child/ sub theme being queried for.
                E.g. `respiratory`.
                Which would filter for `respiratory` under the `theme_name` entity.
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            metric_name: The name of the metric to filter for.
                E.g. `COVID-19_deaths_ONSByDay`.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                Examples:
                    `<APITimeSeriesQuerySet [
                        <APITimeSeries:
                            APITimeSeries for 2023-03-08,
                                              metric 'COVID-19_deaths_ONSByDay',
                                              stratum 'default',
                                              value: 2364.0
                            >,
                            ...
                        ]
                    >`

        """

        queryset = self.filter(
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            geography_type=geography_type_name,
            geography=geography_name,
            metric=metric_name,
        )
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        return self.filter_for_latest_refresh_date_records(queryset=queryset)

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
        latest_refresh_dates_associated_with_dates: APITimeSeriesQuerySet = (
            queryset.values("date").annotate(latest_refresh=models.Max("refresh_date"))
        )

        # Store the latest records for each day so that they can be mapped easily
        # Note that this currently incurs execution of an additional db query
        # The alternative was to possibly use `DISTINCT ON` instead
        # but that is specific to the postgresql backend and would
        # mean we would no longer be agnostic to the underlying database engine.
        # Given the level of caching in the system, the performance penalty incurred
        # here is not noticeable.
        latest_records_map: dict[datetime.datetime.date, datetime.datetime.date] = {
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


class APITimeSeriesManager(models.Manager):
    """Custom model manager class for the `APITimeSeries` model."""

    def get_queryset(self) -> APITimeSeriesQuerySet:
        return APITimeSeriesQuerySet(model=self.model, using=self.db)

    def get_distinct_column_values_with_filters(
        self, lookup_field: str, **kwargs
    ) -> APITimeSeriesQuerySet:
        """Filters for unique values in the column denoted by `lookup_field` via the given **kwargs.

        Args:
            lookup_field: A column to query and retrieve unique values for.
            **kwargs: The filters to apply to the query.

        Returns:
            APITimeSeriesQuerySet: The unique column values as a queryset.
            Examples:
                `<APITimeSeriesQuerySet ['infectious_disease']>`

        """
        return self.get_queryset().get_distinct_column_values_with_filters(
            lookup_field=lookup_field, **kwargs
        )
