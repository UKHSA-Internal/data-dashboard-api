import datetime
import logging
from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.db.models import Manager, QuerySet
from pydantic import BaseModel

from metrics.api.settings import auth
from metrics.data.models.core_models import CoreTimeSeries, Topic
from metrics.domain.common.utils import ChartAxisFields
from metrics.domain.models import (
    ChartRequestParams, PlotGenerationData, PlotParameters,
)
from metrics.domain.models.plots import CompletePlotData
from metrics.interfaces.plots.validation import (
    DatesNotInChronologicalOrderError, MetricDoesNotSupportTopicError,
    PlotValidation,
)
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_TOPIC_MANAGER = Topic.objects

logger = logging.getLogger(__name__)


class DataNotFoundForPlotError(Exception):
    def __init__(self):
        message = "No data was found for the plot requested, please review the plot parameters provided."
        super().__init__(message)


class DataNotFoundForAnyPlotError(Exception):
    def __init__(self):
        message = (
            "No data was found for the plot(s) requested, "
            "please review the request parameters of each plot provided."
        )
        super().__init__(message)


class InvalidPlotParametersError(Exception):
    def __init__(self):
        message = (
            "Invalid plot parameter, "
            "Please check the date range (date_from and date_to) and the topic property provided. "
        )
        super().__init__(message)


class QuerySetResult(BaseModel):
    queryset: Any
    latest_date: Any


class PlotsInterface:
    def __init__(
        self,
        *,
        chart_request_params: ChartRequestParams,
        core_model_manager: CORE_MODEL_MANAGER_TYPE = DEFAULT_CORE_TIME_SERIES_MANAGER,
        topic_model_manager: Manager = DEFAULT_TOPIC_MANAGER,
    ):
        self.chart_request_params = chart_request_params
        self.core_model_manager = core_model_manager
        self.topic_model_manager = topic_model_manager
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
        for plot_parameters in self.chart_request_params.plots:
            validation = PlotValidation(plot_parameters=plot_parameters)
            try:
                validation.validate()
            except (
                MetricDoesNotSupportTopicError,
                DatesNotInChronologicalOrderError,
            ) as error:
                logger.warning(error)
                raise InvalidPlotParametersError from error

    def get_queryset_result_for_plot_parameters(
        self,
        *,
        plot_parameters: PlotParameters,
    ) -> QuerySetResult:
        """Returns the timeseries or headline records for the requested plot as an enriched `QuerySetResult` model.

        Notes:
            If no `date_from` was provided within the `plot_parameters`,
            then a default of 1 year from the current date will be used.

            A `latest_date` attribute is also set
            on the returned `QuerySetResult` model.
            for headline data the `latest_date` is the lastest period end of the
            selected plots.

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

        queryset = self.get_queryset_from_core_model_manager(plot_params=plot_params)

        return QuerySetResult(queryset=queryset, latest_date=queryset.latest_date)

    def get_queryset_from_core_model_manager(
        self,
        plot_params: dict[str, str],
    ):
        """Gets headline or timeseries data based on the `core_model_manager`

        Args:
            plot_params: Dictionary of plot parameters based on the metric type

        Returns:
            QuerySet: Of the latest headline number including:
            Examples:
                `<CoreHeadlineSeriesQuerySet [
                    ('01-04', Decimal('8.0')),
                    ('05-10', Decimal('9.0'))
                ]>`
        """
        if auth.AUTH_ENABLED:
            # Needed for the downstream permissions check
            topic = self.topic_model_manager.get_by_name(name=plot_params["topic"])
            plot_params["theme"] = topic.sub_theme.theme.name
            plot_params["sub_theme"] = topic.sub_theme.name

        return self.core_model_manager.query_for_data(
            **plot_params, rbac_permissions=self.chart_request_params.rbac_permissions
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
            plot_parameters=plot_parameters,
        )

        if not queryset_result.queryset.exists():
            raise DataNotFoundForPlotError

        return CompletePlotData(
            parameters=plot_parameters,
            queryset=queryset_result.queryset,
        )

    def build_plot_data_from_parameters(
        self, *, plot_parameters: PlotParameters
    ) -> PlotGenerationData:
        """Creates a `PlotGenerationData` model which holds the params and data for the given `plot_parameters`

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

        Returns:
            PlotGenerationData: An individual `PlotGenerationData` model
                which holds the parameters and the enriched data
                for the requested individual plot

        Raises:
            `DataNotFoundForPlotError`: If no `CoreTimeSeries` data can be found
                for a particular plot.

        """
        # Set each plot with the selected chart-level x and y-axis choices
        plot_parameters.x_axis = self.chart_request_params.x_axis
        plot_parameters.y_axis = self.chart_request_params.y_axis

        queryset_result: QuerySetResult = self.get_queryset_result_for_plot_parameters(
            plot_parameters=plot_parameters,
        )

        aggregated_results = get_aggregated_results(
            plot_parameters=plot_parameters,
            queryset=queryset_result.queryset,
        )

        return PlotGenerationData.create_from_parameters(
            parameters=plot_parameters,
            aggregated_results=aggregated_results,
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
        for plot_parameters in self.chart_request_params.plots:
            try:
                plot_data: PlotGenerationData = (
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

    def build_plots_data(self) -> list[PlotGenerationData]:
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
        plots_data: list[PlotGenerationData] = []

        for plot_parameters in self.chart_request_params.plots:
            try:
                plot_data: PlotGenerationData = self.build_plot_data_from_parameters(
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
