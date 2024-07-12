import datetime
from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.db.models import Manager, QuerySet
from pydantic import BaseModel

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.common.utils import ChartAxisFields
from metrics.domain.models import PlotData, PlotParameters, PlotsCollection
from metrics.domain.models.plots import CompletePlotData
from metrics.interfaces.plots.validation import (
    DatesNotInChronologicalOrderError,
    MetricDoesNotSupportTopicError,
    PlotValidation,
)

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class DataNotFoundForPlotError(Exception): ...


class DataNotFoundForAnyPlotError(Exception): ...


class InvalidPlotParametersError(Exception): ...


class QuerySetResult(BaseModel):
    queryset: Any
    latest_date: Any


class PlotsInterface:
    def __init__(
        self,
        *,
        plots_collection: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.plots_collection = plots_collection
        self.core_time_series_manager = core_time_series_manager
        self.validate_plot_parameters()

    def validate_plot_parameters(self) -> None:
        """Validates each plot parameters model on the `PlotCollection`

        Returns:
            None

        Raises:
            `InvalidPlotParametersError`: If an underlying
                validation check has failed.
                This could be because there is
                an invalid topic and metric selection.
                Or because the selected dates are not in
                the expected chronological order.

        """
        for plot_parameters in self.plots_collection.plots:
            validation = PlotValidation(plot_parameters=plot_parameters)
            try:
                validation.validate()
            except (
                MetricDoesNotSupportTopicError,
                DatesNotInChronologicalOrderError,
            ) as error:
                raise InvalidPlotParametersError from error

    def get_queryset_result_for_plot_parameters(
        self, *, plot_parameters: PlotParameters
    ) -> QuerySetResult:
        """Returns the timeseries records for the requested plot as an enriched `QuerySetResult` model.

        Notes:
            If no `date_from` was provided within the `plot_parameters`,
            then a default of 1 year from the current date will be used.

            A `latest_date` attribute is also set
            on the returned `QuerySetResult` model.

        Returns:
            QuerySetResult: An enriched object containing
                a) An ordered queryset from oldest -> newest
                    of the (dt, metric_value) numbers.
                    Examples:
                        `<CoreTimeSeriesQuerySet [
                            (datetime.date(2022, 10, 10), Decimal('0.8')),
                            (datetime.date(2022, 10, 17), Decimal('0.9'))
                        ]>`
                b) The latest refresh date associated with the resulting data

        """
        plot_params: dict[str, str] = plot_parameters.to_dict_for_query()
        queryset = self.get_timeseries(**plot_params)

        return QuerySetResult(
            queryset=queryset,
            latest_date=queryset.latest_date,
        )

    def get_timeseries(
        self,
        *,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date | str,
        date_to: datetime.date | None = None,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ):
        """Gets the time series for the `metric` and `topic` from the `date_from` stamp.

        Notes:
            Additional filtering is available via the following optional params:
             - `geography_name`
             - `geography_type_name`
             - `stratum_name`
             - `sex`

        Args:
            x_axis: The field to display along the x-axis
                E.g. `date` or `stratum`
            y_axis: The field to display along the y-axis
                E.g. `metric`
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `COVID-19_deaths_ONSByDay`
            date_from: The datetime object or string to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0) or "2023-03-27"
                would strip off any records which occurred before that date.
            date_to: The datetime object or string to end the query at.
                E.g. datetime.datetime(2023, 6, 28, 0, 0, 0, 0) or "2023-06-28"
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `default`, which would be used to capture all strata
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.
            age: The age range to apply additional filtering to.
                E.g. `0_4` would be used to capture the age of 0-4 years old

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('8.0')),
                        (datetime.date(2022, 10, 17), Decimal('9.0'))
                    ]>`

        """
        return self.core_time_series_manager.query_for_data(
            fields_to_export=[x_axis, y_axis, "in_reporting_delay_period"],
            field_to_order_by=x_axis,
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

    def build_plot_data_from_parameters_with_complete_queryset(
        self, *, plot_parameters: PlotParameters
    ) -> CompletePlotData:
        """Creates a `CompletePlotData` model which holds the params and full queryset for the given requested plot

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

        Returns:
            An individual `CompletePlotData` model
            for the requested `plot_parameters`.

        Raises:
            `DataNotFoundForPlotError`: If no `CoreTimeSeries` data
                can be found for a particular plot.

        """
        queryset_result: QuerySetResult = self.get_queryset_result_for_plot_parameters(
            plot_parameters=plot_parameters
        )

        if not queryset_result.queryset.exists():
            raise DataNotFoundForPlotError

        return CompletePlotData(
            parameters=plot_parameters,
            queryset=queryset_result.queryset,
        )

    def build_plot_data_from_parameters(
        self, *, plot_parameters: PlotParameters
    ) -> PlotData:
        """Creates a `PlotData` model which holds the params and corresponding data for the given requested plot

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

        Returns:
            PlotData: An individual `PlotData` models f
                or the requested `plot_parameters`.

        Raises:
            `DataNotFoundForPlotError`: If no `CoreTimeSeries` data can be found
                for a particular plot.

        """
        # Set each plot with the selected chart-level x and y-axis choices
        plot_parameters.x_axis = self.plots_collection.x_axis
        plot_parameters.y_axis = self.plots_collection.y_axis

        queryset_result: QuerySetResult = self.get_queryset_result_for_plot_parameters(
            plot_parameters=plot_parameters
        )

        aggregated_results = get_aggregated_results(
            plot_parameters=plot_parameters, queryset=queryset_result.queryset
        )

        return PlotData(
            parameters=plot_parameters,
            x_axis_values=aggregated_results[plot_parameters.x_axis_value],
            y_axis_values=aggregated_results[plot_parameters.y_axis_value],
            latest_date=queryset_result.latest_date,
        )

    def build_plots_data_for_full_queryset(self) -> list[CompletePlotData]:
        """Creates a list of `CompletePlotData` models which hold the params and corresponding data for the plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that plot is skipped and no enriched model will be provided.

        Returns:
            A list of `CompletePlotData` models for
            each of the requested plots.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        plots_data: list[CompletePlotData] = []
        for plot_parameters in self.plots_collection.plots:
            try:
                plot_data: PlotData = (
                    self.build_plot_data_from_parameters_with_complete_queryset(
                        plot_parameters=plot_parameters
                    )
                )
            except DataNotFoundForPlotError:
                continue

            plots_data.append(plot_data)

        if not plots_data:
            raise DataNotFoundForAnyPlotError

        return plots_data

    def build_plots_data(self) -> list[PlotData]:
        """Creates a list of `PlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that plot is skipped and no enriched model is provided.

        Returns:
            List[PlotData]: A list of `PlotData` models for
                each of the requested plots.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        plots_data: list[PlotData] = []
        for plot_parameters in self.plots_collection.plots:
            try:
                plot_data: PlotData = self.build_plot_data_from_parameters(
                    plot_parameters=plot_parameters
                )
            except DataNotFoundForPlotError:
                continue

            plots_data.append(plot_data)

        if not plots_data:
            raise DataNotFoundForAnyPlotError

        return plots_data


def get_aggregated_results(
    *, plot_parameters: PlotParameters, queryset: QuerySet
) -> dict[str, list[datetime.date | Decimal | bool | str]]:
    """Gets the aggregated results for a given `queryset` based on the `plot_parameters`

    Args:
        plot_parameters: A `PlotParameters` model containing
            the requested info
        queryset: An ordered queryset from oldest -> newest
            of the (dt, metric_value) numbers.
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

    Returns:
        Dict containing the field names valued by the list of results.
        E.g.
        >>> {
                "date": [(datetime.date(2022, 10, 10), ...],
                "metric_value: [Decimal('0.8'), ...],
                "in_reporting_delay_period": [False, ...]
            }

    """
    if plot_parameters.x_axis == ChartAxisFields.age.name:
        result = aggregate_results_by_age(queryset=queryset)
    else:
        result = aggregate_results(values=queryset)

    if not result:
        raise DataNotFoundForPlotError

    return result


def convert_type(*, s: str) -> int | str:
    """
    Convert a string to a number if possible

    Args:
        s: A string that may or may not be a number

    Returns:
        The input as a number or the string itself.
        This is converted to lowercase, so it sorts as one would expect

    """
    return int(s) if s.isdigit() else s.lower()


def aggregate_results_by_age(*, queryset: QuerySet) -> dict[str, list[str | Decimal]]:
    """Age values are cast to human-readable strings and aggregated

    Args:
        queryset: An iterable containing a list of dicts where
            Age is the first value and the metric value is the second
            E.g. {"age__name": "15_44", "metric_value": "Decimal('0.7')}

    Returns:
        A properly sorted and displayable version broken into two separate lists

    """
    for exported_result in queryset:
        age: str = exported_result[ChartAxisFields.age.value]
        exported_result[ChartAxisFields.age.value] = _build_age_display_name(value=age)

    return aggregate_results(values=queryset)


def _build_age_display_name(*, value: str) -> str:
    return value.replace("-", " - ")


def aggregate_results(*, values) -> dict[str, list[datetime.date | Decimal | bool]]:
    """Aggregates the `values` as a dict of nested lists

    Args:
        `values`: The list of things to zip

    Returns:
        An aggregated dict of nested lists
        >>> {
                "date": [(datetime.date(2022, 10, 10), ...],
                "metric_value: [Decimal('0.8'), ...],
                "in_reporting_delay_period": [False, ...]
        }

    """
    aggregated_results = defaultdict(list)

    for row in values:
        for key, value in row.items():
            aggregated_results[key].append(value)

    return dict(aggregated_results)
