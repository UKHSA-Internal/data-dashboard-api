import datetime
from typing import Dict, List, Optional

from django.db.models import Manager

from metrics.data.access.core_models import (
    get_date_n_months_ago_from_timestamp,
    unzip_values,
)
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import TablePlotParameters, TablePlots, TabularPlotData
from metrics.domain.tables.generation import create_plots_in_tabular_format
from metrics.interfaces.tables import validation

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class DataNotFoundError(ValueError):
    ...


class TablesInterface:
    def __init__(
        self,
        table_plots: TablePlots,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.table_plots = table_plots
        self.core_time_series_manager = core_time_series_manager

    def build_table_plots_data(self) -> List[TabularPlotData]:
        """Creates a list of `TablesPlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and an enriched model is not provided.

        Returns:
            List[TabularPlotData]: A list of `TabularPlotData` models for
                each of the requested table plots.

        """
        table_plots_data: List[TabularPlotData] = []
        for table_plot_parameters in self.table_plots.plots:
            try:
                chart_plot_data = self.build_table_plot_data_from_parameters(
                    table_plot_parameters=table_plot_parameters
                )
            except DataNotFoundError:
                continue

            table_plots_data.append(chart_plot_data)

        return table_plots_data

    def build_table_plot_data_from_parameters(
        self, table_plot_parameters: TablePlotParameters
    ):
        """Creates a `TabularPlotData` model which holds the params and corresponding data for the given requested plot

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

        Returns:
            List[TabularPlotData]: A list of `TabularPlotData` models for
                each of the requested table plots.

        Raises:
            `DataNotFoundError`: If no `CoreTimeSeries` data can be found
                for a particular plot.

        """
        timeseries_queryset = self.get_timeseries_for_table_plot_parameters(
            table_plot_parameters=table_plot_parameters
        )

        try:
            x_axis_values, y_axis_values = unzip_values(timeseries_queryset)
        except ValueError as error:
            raise DataNotFoundError from error
        else:
            return TabularPlotData(
                parameters=table_plot_parameters,
                x_axis_values=x_axis_values,
                y_axis_values=y_axis_values,
            )

    def get_timeseries_for_table_plot_parameters(
        self, table_plot_parameters: TablePlotParameters
    ):
        """Returns the timeseries records for the requested plot as a QuerySet

        Notes:
            If no `date_from` was provided within the `table_plot_parameters`,
            then a default of 1 year from the current date will be used.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers.
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        plot_params: Dict[str, str] = table_plot_parameters.to_dict_for_query()
        date_from: str = make_datetime_from_string(
            date_from=table_plot_parameters.date_from
        )

        return self.get_timeseries(
            **plot_params,
            date_from=date_from,
        )

    def get_timeseries(
        self,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        geography_name: Optional[str] = None,
        geography_type_name: Optional[str] = None,
        stratum_name: Optional[str] = None,
    ):
        """Gets the time series for the `metric_name` and `topic_name` from the `date_from` stamp.

        Notes:
            Additional filtering is available via the following optional params:
             - `geography_name`
             - `geography_type_name`
             - `stratum_name`

        Args:
            topic_name: The name of the disease being queried.
                E.g. `COVID-19`
            metric_name: The name of the metric being queried.
                E.g. `new_cases_7days_sum
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `0_4`, which would be used to capture the age group 0 to 4 years old.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        return self.core_time_series_manager.filter_for_dates_and_values(
            topic_name=topic_name,
            metric_name=metric_name,
            date_from=date_from,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
        )

    def generate_plots_for_table(self) -> List[Dict[str, str]]:
        """Create a list of plots from the request

        Returns:
            The requested plots in tabular format
        """
        plots_data: List[TabularPlotData] = self.build_table_plots_data()

        return create_plots_in_tabular_format(
            tabular_plots_data=plots_data,
        )


def generate_tabular_output(table_plots: TablePlots) -> List[Dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `table_plots` model

    Args:
        table_plots: The requested table plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric_name` is not
            compatible for the required `topic`.
            E.g. `new_cases_daily` is currently only available
            for the topic of `COVID-19`
    """
    validate_each_requested_table_plot(table_plots=table_plots)

    library = TablesInterface(table_plots=table_plots)
    tabular_output = library.generate_plots_for_table()

    return tabular_output


def validate_each_requested_table_plot(table_plots: TablePlots) -> None:
    """Validates the request table plots against the contents of the db

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric_name` is not
            compatible for the required `topic`.
            E.g. `new_cases_daily` is currently only available
            for the topic of `COVID-19`

    """
    for table_plot_params in table_plots.plots:
        validate_table_plot_parameters(table_plot_parameters=table_plot_params)


def validate_table_plot_parameters(table_plot_parameters: TablePlotParameters):
    """Validates the individual given `chart_plot_parameters` against the contents of the db

    Raises:
        `ChartTypeDoesNotSupportMetricError`: If the `metric_name` is not
            compatible for the required `chart_type`.
            E.g. A cumulative headline type number like `positivity_7days_latest`
            would not be viable for a line type (timeseries) chart.

        `MetricDoesNotSupportTopicError`: If the `metric_name` is not
            compatible for the required `topic`.
            E.g. `new_cases_daily` is currently only available
            for the topic of `COVID-19`

    """
    date_from = make_datetime_from_string(date_from=table_plot_parameters.date_from)
    tables_request_validator = validation.TablesRequestValidator(
        topic_name=table_plot_parameters.topic_name,
        metric_name=table_plot_parameters.metric_name,
        date_from=date_from,
    )
    tables_request_validator.validate()


def make_datetime_from_string(date_from: Optional[str]) -> datetime.datetime:
    """Parses the `date_from` string into a datetime object. Defaults to 1 year ago from the current date.

    Args:
        date_from: A string representing the date in the format `%Y-%m-%d`
            E.g. "2022-10-01"

    Returns:
        `datetime` object representing the `date_from` string
            or a default of 1 year ago from the current date.

    """
    try:
        return datetime.datetime.strptime(date_from, "%Y-%m-%d")
    except (TypeError, ValueError):
        one_year = 12
        return get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime.date.today(), number_of_months=one_year
        )
