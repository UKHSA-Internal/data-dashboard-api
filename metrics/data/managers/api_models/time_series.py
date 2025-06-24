"""
This file contains the custom QuerySet and Manager classes associated with the `APITimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from typing import Self

from django.db import models
from django.db.models.functions.window import Rank
from django.utils import timezone


class APITimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `APITimeSeriesManager`"""

    @property
    def partition_fields(self) -> list[str]:
        return ["age", "sex", "stratum", "date"]

    def get_distinct_column_values_with_filters(
        self, *, lookup_field: str, restrict_to_public: bool, **kwargs
    ) -> "APITimeSeriesQuerySet":
        """Filters for unique values in the column denoted by `lookup_field` via the given **kwargs.

        Args:
            lookup_field: A column to query and retrieve unique values for.
            restrict_to_public: Boolean switch to restrict the query
                to only return public records.
                If False, then non-public records will be included.
            **kwargs: The filters to apply to the query.

        Returns:
            APITimeSeriesQuerySet: The unique column values as a queryset.
            Examples:
                `<APITimeSeriesQuerySet ['infectious_disease']>`

        """
        queryset = self.filter(**kwargs)
        if restrict_to_public:
            queryset = queryset.filter(is_public=True)

        return queryset.values_list(lookup_field, flat=True).distinct()

    def filter_for_audit_list_view(
        self,
        *,
        metric: str,
        geography_type: str,
        geography: str,
        stratum: str,
        sex: str,
        age: str,
    ) -> "APITimeSeriesQuerySet":
        """Filters for all records based on the provided arguments including `metric`, `geography` etc.
            returns all records including those under `embargo` or `stale/duplicated` records.

        Args:
            metric: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            geography: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old
        """
        return self.filter(
            metric=metric,
            geography_type=geography_type,
            geography=geography,
            stratum=stratum,
            sex=sex,
            age=age,
        )

    def filter_for_list_view(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        geography_type: str,
        geography: str,
        metric: str,
        restrict_to_public: bool,
    ) -> Self:
        """Filters by the given fields to provide a slice of the timeseries data as per the fields.

        Args:
            theme: The name of the root theme being queried for.
                E.g. `infectious_disease`
            sub_theme: The name of the child/ sub theme being queried for.
                E.g. `respiratory`.
                Which would filter for `respiratory` under the `theme_name` entity.
            topic_name: The name of the disease being queried.
                Which would filter for `respiratory` under the `theme` entity.
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            geography_type: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            geography: The name of the geography to apply additional filtering to.
                E.g. `England`
            metric: The name of the metric to filter for.
                E.g. `COVID-19_deaths_ONSByDay`.
            restrict_to_public: Boolean switch to restrict the query
                to only return public records.
                If False, then non-public records will be included.

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
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            geography_type=geography_type,
            geography=geography,
            metric=metric,
        )
        if restrict_to_public:
            queryset = queryset.filter(is_public=True)

        queryset = self._exclude_data_under_embargo(queryset=queryset)
        return self.filter_for_latest_refresh_date_records(queryset=queryset)

    def filter_for_latest_refresh_date_records(self, *, queryset: Self) -> Self:
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
            for the individual dates.

            This will partition the `queryset`
            and returns records with the latest `refresh_date`
            from each window

        Args:
            queryset: The queryset to filter against

        Returns:
            A new filtered queryset containing
            only the latest records for each date

        """
        # Filter the queryset to get records with a ranking of 1.
        # This will return the records with the latest `refresh_date` within each partition
        queryset = self._partition_and_rank_data(
            queryset=queryset, partition_fields=self.partition_fields
        )
        return queryset.filter(refresh_ranking=1)

    def filter_for_outdated_refresh_date_records(self, *, queryset: Self) -> Self:
        """Grabs all stale records which are not under embargo

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

            This will partition the `queryset`
            and returns records which do not have
            the latest `refresh_date` from each window

        Args:
            queryset: The queryset to filter against

        Returns:
            A new filtered queryset containing
            only the stale records for each date

        """
        # Filter the queryset to get records with a ranking of greater than 1.
        # This will return the records with outdated `refresh_dates` within each partition
        queryset = self._partition_and_rank_data(
            queryset=queryset, partition_fields=self.partition_fields
        )
        return queryset.filter(refresh_ranking__gt=1)

    @classmethod
    def _partition_and_rank_data(
        cls, *, queryset: Self, partition_fields: list[str]
    ) -> Self:
        # Use the window function to annotate
        # the rank of each record within its partition
        window = models.Window(
            expression=Rank(),
            partition_by=partition_fields,
            order_by=models.F("refresh_date").desc(),
        )

        # Annotate each record with a calculated ranking.
        # Whereby the `refresh_ranking` is determined by the latest `refresh_date`
        return queryset.annotate(refresh_ranking=window)

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

    def query_for_superseded_data(
        self,
        *,
        theme_name: str,
        sub_theme_name: str,
        topic_name: str,
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
           theme_name: The name of the parent theme being queried.
               E.g. `infectious_disease`
           sub_theme_name: The name of the child theme being queried.
               E.g. `respiratory`
           topic_name: The name of the threat being queried.
               E.g. `COVID-19`
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
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            metric=metric_name,
            geography=geography_name,
            geography_code=geography_code,
            geography_type=geography_type_name,
            stratum=stratum_name,
            age=age,
            sex=sex,
            is_public=is_public,
        )
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        queryset = self.filter_for_outdated_refresh_date_records(queryset=queryset)

        # Note that we cannot call `delete()` on the above queryset.
        # This is because it uses the `WINDOW` function.
        # Which is not allowed with a `DELETE` statement.
        # So we need to filter by IDs first.
        superseded_record_ids = queryset.values_list("id", flat=True)
        return self.filter(id__in=superseded_record_ids)


class APITimeSeriesManager(models.Manager):
    """Custom model manager class for the `APITimeSeries` model."""

    def get_queryset(self) -> APITimeSeriesQuerySet:
        return APITimeSeriesQuerySet(model=self.model, using=self.db)

    def get_distinct_column_values_with_filters(
        self, *, lookup_field: str, restrict_to_public: bool, **kwargs
    ) -> APITimeSeriesQuerySet:
        """Filters for unique values in the column denoted by `lookup_field` via the given **kwargs.

        Args:
            lookup_field: A column to query and retrieve unique values for.
            restrict_to_public: Boolean switch to restrict the query
                to only return public records.
                If False, then non-public records will be included.
            **kwargs: The filters to apply to the query.

        Returns:
            APITimeSeriesQuerySet: The unique column values as a queryset.
            Examples:
                `<APITimeSeriesQuerySet ['infectious_disease']>`

        """
        return self.get_queryset().get_distinct_column_values_with_filters(
            lookup_field=lookup_field, restrict_to_public=restrict_to_public, **kwargs
        )

    def query_for_superseded_data(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str,
        stratum: str,
        sex: str,
        age: str,
        is_public: bool,
    ) -> APITimeSeriesQuerySet:
        """Grabs all stale records which are not under embargo.

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

            This will partition the `queryset`
            and returns records which do not have
            the latest `refresh_date` from each window

        Args:
           theme: The name of the parent theme being queried.
               E.g. `infectious_disease`
           sub_theme: The name of the child theme being queried.
               E.g. `respiratory`
           topic: The name of the threat being queried.
               E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-COVID-19_cases_countRollingMean`
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
        return self.get_queryset().query_for_superseded_data(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            sex=sex,
            age=age,
            is_public=is_public,
        )

    def delete_superseded_data(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str,
        stratum: str,
        sex: str,
        age: str,
        is_public: bool,
    ) -> APITimeSeriesQuerySet:
        """Deletes all stale records which are not under embargo.

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

            This will partition the `queryset`
            and deletes all records which do not have
            the latest `refresh_date` from each window

        Args:
           theme: The name of the parent theme being queried.
               E.g. `infectious_disease`
           sub_theme: The name of the child theme being queried.
               E.g. `respiratory`
           topic: The name of the threat being queried.
               E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-COVID-19_cases_countRollingMean`
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
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            sex=sex,
            age=age,
            is_public=is_public,
        )
        superseded_records.delete()
