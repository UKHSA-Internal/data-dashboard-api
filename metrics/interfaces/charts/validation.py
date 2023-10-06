from typing import Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, Metric
from metrics.domain.models import PlotParameters
from metrics.domain.utils import ChartTypes
from metrics.interfaces.plots.validation import PlotValidation

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_METRIC_MANAGER = Metric.objects


class ChartTypeDoesNotSupportMetricError(Exception):
    ...


class ChartsRequestValidator:
    def __init__(
        self,
        plot_parameters: PlotParameters,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
        plot_validation: Optional[PlotValidation] = None,
    ):
        self.plot_parameters = plot_parameters
        self.core_time_series_manager = core_time_series_manager
        self.metric_manager = metric_manager

        self.plot_validation = plot_validation or PlotValidation(
            plot_parameters=plot_parameters,
            core_time_series_manager=core_time_series_manager,
            metric_manager=metric_manager,
        )

    def validate(self) -> None:
        """Validates the request against the contents of the db

        Raises:
            `ChartTypeDoesNotSupportMetricError`: If the `metric` is not
                compatible for the required `chart_type`.
                E.g. A cumulative headline type number like `positivity_7days_latest`
                would not be viable for a line type (timeseries) chart.

            `MetricDoesNotSupportTopicError`: If the `metric` is not
                compatible for the required `topic`.
                E.g. `COVID-19_deaths_ONSByDay` is only available
                for the topic of `COVID-19`

            `DatesNotInChronologicalOrderError`: If a provided `date_to`
                is chronologically behind the provided `date_from`.
                E.g. date_from = datetime.datetime(2022, 10, 2)
                    & date_to = datetime.datetime(2021, 8, 1)
                Note that if None is provided to `date_to`
                then this error will not be raised.

        """
        # Chart-specific validations
        self._validate_series_type_chart_works_with_metric()

        # Common validations delegated to the `PlotValidation` object
        self.plot_validation.validate()

    def _is_chart_series_type(self) -> bool:
        """Checks if the instance variable `chart_type` is of a timeseries type.

        Returns:
            bool: True if the `chart_type` can be used for timeseries data.
                False otherwise

        """
        if self.plot_parameters.chart_type == ChartTypes.waffle.value:
            return False
        return True

    def _validate_series_type_chart_works_with_metric(self) -> None:
        requested_chart_is_series_type = self._is_chart_series_type()
        if not requested_chart_is_series_type:
            return

        metric_is_series_chart_compatible: bool = (
            self.plot_validation.does_metric_have_multiple_records()
        )
        if not metric_is_series_chart_compatible:
            raise ChartTypeDoesNotSupportMetricError(
                f"`{self.plot_parameters.metric_name}` "
                f"is not compatible with `{self.plot_parameters.chart_type}` chart types"
            )
