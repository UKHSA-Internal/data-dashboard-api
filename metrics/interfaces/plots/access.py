import datetime
from typing import Dict, List, Optional, Tuple, Union

from django.db.models import Manager, QuerySet

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import PlotParameters, PlotsCollection, PlotData
from metrics.domain.utils import ChartAxisFields

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class DataNotFoundError(ValueError):
    ...


class PlotsInterface:
    def __init__(
        self,
        plots_collection: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.plots_collection = plots_collection
        self.core_time_series_manager = core_time_series_manager

    def get_timeseries_for_plot_parameters(self, plot_parameters: PlotParameters):
        """Returns the timeseries records for the requested plot as a QuerySet

        Notes:
            If no `date_from` was provided within the `plot_parameters`,
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
        plot_params: Dict[str, str] = plot_parameters.to_dict_for_query()
        return self.get_timeseries(**plot_params)

    def get_timeseries(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: Union[datetime.date, str],
        geography_name: Optional[str] = None,
        geography_type_name: Optional[str] = None,
        stratum_name: Optional[str] = None,
        sex: Optional[str] = None,
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
                E.g. `new_cases_7days_sum`
            date_from: The datetime object or string to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0) or "2023-03-27"
                would strip off any records which occurred before that date.
            geography_name: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type_name: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum_name: The value of the stratum to apply additional filtering to.
                E.g. `0_4`, which would be used to capture the age group 0 to 4 years old.
            sex: The gender to apply additional filtering to.
                E.g. `F`, would be used to capture Females.
                Note that options are `M`, `F`, or `ALL`.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        return self.core_time_series_manager.filter_for_x_and_y_values(
            x_axis=x_axis,
            y_axis=y_axis,
            topic_name=topic_name,
            metric_name=metric_name,
            date_from=date_from,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
            sex=sex,
        )

    def build_plot_data_from_parameters(
        self, plot_parameters: PlotParameters
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
            `DataNotFoundError`: If no `CoreTimeSeries` data can be found
                for a particular plot.

        """
        timeseries_queryset = self.get_timeseries_for_plot_parameters(
            plot_parameters=plot_parameters
        )

        try:
            x_axis_values, y_axis_values = get_x_and_y_values(
                plot_parameters=plot_parameters, queryset=timeseries_queryset
            )
        except ValueError as error:
            raise DataNotFoundError from error

        return PlotData(
            parameters=plot_parameters,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
        )

    def build_plots_data(self) -> List[PlotData]:
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

        """
        plots_data: List[PlotData] = []
        for plot_parameters in self.plots_collection.plots:
            try:
                plot_data: PlotData = self.build_plot_data_from_parameters(
                    plot_parameters=plot_parameters
                )
            except DataNotFoundError:
                continue

            plots_data.append(plot_data)

        return plots_data


def get_x_and_y_values(
    plot_parameters: PlotParameters, queryset: QuerySet
) -> Tuple[List, List]:
    """Gets the X and Y values for a given `queryset` based on the `plot_parameters`

    Args:
        plot_parameters: A `PlotParameters` model containing
            the requested info
        queryset:

    Returns:

    """

    # Stratum needs special treatment because a regular sort does not yield the required result
    if plot_parameters.x_axis == ChartAxisFields.stratum.name:
        return sort_by_stratum(queryset=queryset)

    return unzip_values(values=queryset)


def sort_by_stratum(queryset: QuerySet) -> Tuple[List, List]:
    """
    Take a list of tuples where Stratum is the first element, sort it, prettify the stratum values and return as two separate lists

    Args:
        queryset: A queryset containing a list of tuples where Stratum is the first value and the metric value is the second
        E.g. ('15_44', Decimal('0.7'))

    Returns:
        A properly sorted and displayable version broken into two separate lists
    """
    # Make a dictionary where the key is a tuple of the stratum values. So, 45_54 becomes (45, 54) etc
    temp_dict = {tuple(map(int, x[0].replace("+", "").split("_"))): x for x in queryset}

    # Now sort on the tuple and return the x and y values
    # Change the Stratum so it looks nice. eg. 0_4 becomes 0-4
    x_values = [temp_dict[x][0].replace("_", "-") for x in sorted(temp_dict.keys())]
    y_values = [temp_dict[x][1] for x in sorted(temp_dict.keys())]

    return x_values, y_values


def unzip_values(values) -> Tuple[List, List]:
    """
    Take a list and zip it

    Args:
        The list of things to zip

    Returns:
        A zipped version of the `values``

    """
    return zip(*values)
