"""
This file contains the custom QuerySet and Manager classes associated with the `APITimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""


from django.db import models


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
                E.g. `new_cases_daily`.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest"
                Examples:
                    `<APITimeSeriesQuerySet [
                        <APITimeSeries:
                            APITimeSeries for 2023-03-08,
                                              metric 'new_cases_daily',
                                              stratum 'default',
                                              value: 2364.0
                            >,
                            ...
                        ]
                    >`

        """

        return self.filter(
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            geography_type=geography_type_name,
            geography=geography_name,
            metric=metric_name,
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
