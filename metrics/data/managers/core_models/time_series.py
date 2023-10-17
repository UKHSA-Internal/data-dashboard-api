"""
This file contains the custom QuerySet and Manager classes associated with the `CoreTimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
import datetime
from decimal import Decimal

from django.db import models


class CoreTimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `CoreTimeSeriesManager`"""

    @staticmethod
    def _newest_to_oldest(queryset: models.QuerySet) -> models.QuerySet:
        return queryset.order_by("-date")

    @staticmethod
    def _ascending_order(queryset: models.QuerySet, field_name: str) -> models.QuerySet:
        return queryset.order_by(field_name)

    def by_topic_metric_for_dates_and_values(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
    ) -> models.QuerySet:
        """Filters by the given `topic_name` and `metric_name`. Slices all values older than the `date_from`.

        Args:
            x_axis: The field to display along the x-axis
                E.g. `date` or `stratum`
            y_axis: The field to display along the y-axis
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
        ).values_list(x_axis, y_axis)

        return self._ascending_order(
            queryset=queryset,
            field_name=x_axis,
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

        queryset = queryset.values_list(x_axis, y_axis)
        queryset = self._ascending_order(
            queryset=queryset,
            field_name=x_axis,
        )
        return self._set_latest_refresh_date_on_queryset(queryset=queryset)

    @staticmethod
    def _set_latest_refresh_date_on_queryset(
        queryset: models.QuerySet,
    ) -> models.QuerySet:
        """Sets a `latest_refresh_date` attribute on the given `queryset`

        Notes:
            The `latest_refresh_date` attribute is set according to
            the latest/maximum date associated with any of the records
            returned within the given `queryset`.
            This is a custom attribute, so this must be the final queryset operation.
            If additional filtering is performed, then this attribute will be lost

        Args:
            queryset: The queryset to be labelled with
                the `latest_refresh_date` attribute

        Returns:
            The queryset which has been labelled with
            the `latest_refresh_date` attribute

        """
        latest_refresh_date_aggregation = queryset.aggregate(
            latest_refresh_date=models.Max("refresh_date")
        )
        queryset.latest_refresh_date = latest_refresh_date_aggregation[
            "latest_refresh_date"
        ]
        return queryset

    def by_topic_metric_ordered_from_newest_to_oldest(
        self, topic_name: str, metric_name: str
    ) -> models.QuerySet:
        """Filters by the given `topic_name` and `metric_name`. Slices all values older than the `date_from`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the individual metric_value numbers only:
                Examples:
                    `<CoreTimeSeriesQuerySet [ Decimal('2.0'), Decimal('9.0')]>`

        """
        queryset = self.filter(
            metric__topic__name=topic_name,
            metric__name=metric_name,
        ).values_list("metric_value", flat=True)
        return self._newest_to_oldest(queryset=queryset)

    def get_metric_value(self, topic_name: str, metric_name: str) -> "CoreTimeSeries":
        """Gets the record associated with the given `topic_name` and `metric_name`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_headline_ONSdeaths_7DayTotals`

        Returns:
            QuerySet: A queryset containing the single record
                Examples:
                    `<CoreTimeSeries:
                        Core Data for 2023-03-04,
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

    def by_topic_metric_ordered_from_newest(
        self, topic_name: str, metric_name: str
    ) -> CoreTimeSeriesQuerySet:
        """Filters by the given `topic_name` and `metric_name`. Slices all values older than the `date_from`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`

        Returns:
            QuerySet: An ordered queryset from newest -> oldest
                of the individual metric_value numbers only:
                Examples:
                    `<CoreTimeSeriesQuerySet [Decimal('2.0'), Decimal('9.0')]>`

        """
        return self.get_queryset().by_topic_metric_ordered_from_newest_to_oldest(
            topic_name=topic_name, metric_name=metric_name
        )

    def get_latest_metric_value(
        self, topic_name: str, metric_name: str
    ) -> Decimal | None:
        """Grabs by the latest record by the given `topic_name` and `metric_name`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`

        Returns:
            Optional[Decimal]: The individual metric_value number only.
                Otherwise, None is returned if no record could be found
                Examples:
                    `2.0`

        """
        return (
            self.get_queryset()
            .by_topic_metric_ordered_from_newest_to_oldest(
                topic_name=topic_name, metric_name=metric_name
            )
            .first()
        )

    def by_topic_metric_for_dates_and_values(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
    ) -> CoreTimeSeriesQuerySet:
        """Filters by the given `topic_name` and `metric_name`. Slices all values older than the `date_from`.

        Args:
            x_axis: The field to display along the x-axis
                E.g. `date` or `stratum`
            y_axis: The field to display along the y-axis
                E.g. `metric`
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.

        Returns:
            QuerySet: An ordered queryset from lowest -> highest
                of the (x_axis, y_axis) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('8.0')),
                        (datetime.date(2022, 10, 17), Decimal('9.0'))
                    ]>`

        """
        return self.get_queryset().by_topic_metric_for_dates_and_values(
            x_axis=x_axis,
            y_axis=y_axis,
            topic_name=topic_name,
            metric_name=metric_name,
            date_from=date_from,
            date_to=date_to,
        )

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

    def get_count(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
    ) -> int:
        """Gets the number of records which match the given `topic_name` and `metric_name`, newer than `date_from`

        Args:
            x_axis: The field to display along the x-axis
                E.g. `date` or `stratum`
            y_axis: The field to display along the y-axis
                E.g. `metric`
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
            date_to: The datetime object to end the query at.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would cut any records which occurred after that date.

        Returns:
            int: The count of the number of `CoreTimeSeries` records which match the criteria

        """
        return self.by_topic_metric_for_dates_and_values(
            x_axis=x_axis,
            y_axis=y_axis,
            topic_name=topic_name,
            metric_name=metric_name,
            date_from=date_from,
            date_to=date_to,
        ).count()

    def get_metric_value(self, topic_name: str, metric_name: str) -> Decimal:
        """Gets the record associated with the given `topic_name` and `metric_name`.

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_headline_ONSdeaths_7DayTotals`

        Returns:
            QuerySet: A queryset containing the single record
                Examples:
                    `<CoreTimeSeries:
                        Core Data for 2023-03-04,
                        metric 'COVID-19_headline_ONSdeaths_7DayTotals',
                        value: 24298.0
                    >`

        Raises:
            `MultipleObjectsReturned`: If the query returned more than 1 record.
                We expect this if the provided `metric` is for timeseries type data

            `DoesNotExist`: If the query returned no records.

        """
        model_instance = self.get_queryset().get_metric_value(
            topic_name=topic_name, metric_name=metric_name
        )
        return model_instance.metric_value

    def get_all_sex_names(self) -> models.QuerySet:
        """Gets all available sex names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sex names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<CoreTimeSeriesQuerySet [('ALL'), ('F'), ('M')]>`

        """
        return self.get_queryset().get_all_sex_names()
