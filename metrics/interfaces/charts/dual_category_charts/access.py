from datetime import datetime

import plotly.graph_objects as go

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.charts.stacked_bar.generation import generate_stacked_bar
from metrics.domain.common.utils import (
    extract_metric_group_from_metric,
)
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
)
from metrics.domain.models.plots import (
    ChartGenerationPayload,
    PlotGenerationData,
)
from metrics.domain.models.plots_text import PlotsText
from metrics.interfaces.charts.common.chart_output import ChartOutput
from metrics.interfaces.plots.access import PlotsInterface
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class DualCategoryChartsInterface:
    def __init__(
        self,
        *,
        chart_request_params: DualCategoryChartRequestParams,
        core_model_manager: CORE_MODEL_MANAGER_TYPE | None = None,
        plots_interface: PlotsInterface | None = None,
    ):
        self.chart_request_params = chart_request_params
        self.chart_type = self.chart_request_params.chart_type
        self.metric_group = extract_metric_group_from_metric(
            metric=self.chart_request_params.static_fields.metric,
        )
        self.core_model_manager = core_model_manager or self._set_core_model_manager()
        self.plots_interface = plots_interface or PlotsInterface(
            chart_request_params=self.chart_request_params,
            core_model_manager=self.core_model_manager,
        )

        self.last_updated: str = ""

    @property
    def is_headline_data(self) -> bool:
        return self.chart_request_params.plots[0].is_headline_data

    @staticmethod
    def _build_chart_figure(
        chart_generation_payload: ChartGenerationPayload,
    ) -> go.Figure:
        """Build a Plotly chart `Figure` object for a `DualCategory` chart.

        Args:
            chart_generation_payload: An enriched `ChartGenerationPayload` model
                which holds all the parameters like colour and plot labels
                 along with the corresponding x and y values
                 which are needed to be able to generate the chart in full.

        Returns:
            A plotly `Figure` object for the created dual-category chart.
        """
        return generate_stacked_bar(
            chart_generation_payload=chart_generation_payload,
        )

    def _build_chart_plots_data(self) -> list[PlotGenerationData]:
        """Creates a list of `PlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and
            an enriched model will not be provided.

        Returns:
            A list of `PlotData` models for each of the requested chart plots.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        plots_data: list[PlotGenerationData] = self.plots_interface.build_plots_data()
        self._set_latest_date_from_plots_data(plots_data=plots_data)

        return plots_data

    def _set_latest_date_from_plots_data(
        self, *, plots_data: list[PlotGenerationData]
    ) -> None:
        """Extracts the latest date from the list of given `plots_data`

        Notes:
            This extracted value is set on the `_latest_date`
            instance attribute on this object

        Args:
            plots_data: List of `PlotData` models,
                where each model represents a requested plot.
                Note that each `PlotData` model is enriched
                with the according x and y values along with
                requests parameters like colour and plot label.

        Returns:
            None

        """
        try:
            latest_date: datetime.date = max(plot.latest_date for plot in plots_data)
        except (ValueError, TypeError):
            return

        self.last_updated: str = datetime.strftime(latest_date, "%Y-%m-%d")

    def _build_chart_generation_payload(self) -> ChartGenerationPayload:
        plots_data: list[PlotGenerationData] = self._build_chart_plots_data()

        return ChartGenerationPayload(
            plots=plots_data,
            x_axis_title=self.chart_request_params.x_axis_title,
            y_axis_title=self.chart_request_params.y_axis_title,
            chart_height=self.chart_request_params.chart_height,
            chart_width=self.chart_request_params.chart_width,
            y_axis_minimum_value=self.chart_request_params.y_axis_minimum_value,
            y_axis_maximum_value=self.chart_request_params.y_axis_maximum_value,
            legend_title=self.chart_request_params.legend_title,
            confidence_intervals=self.chart_request_params.confidence_intervals,
            confidence_colour=self.chart_request_params.confidence_colour,
            secondary_category=self.chart_request_params.secondary_category,
        )

    def _set_core_model_manager(self) -> bool:
        """Returns `core_model_manger` based on the `metric_group`.

        Notes:
            The charts interface can be used to generate charts for
            either `CoreTimeSeries` or `CoreHeadline` data.
            this function returns the Django manager to match the
            current `metric_group` or defaults to `CoreTimeSeries`
            manager.

        Returns:
            Manager: either `CoreTimeSeries` or `CoreHeadline`
        """
        if self.is_headline_data:
            return DEFAULT_CORE_HEADLINE_MANAGER

        return DEFAULT_CORE_TIME_SERIES_MANAGER

    @classmethod
    def build_chart_description(cls, *, plots_data: list[PlotGenerationData]) -> str:
        """Creates a description to summarize the contents of the chart.

        Args:
            plots_data: List of `PlotData` models,
                where each model represents a requested plot.
                Note that each `PlotData` model is enriched with data
                with the according x and y values along with
                requests parameters like colour and plot label.

        Returns:
            Single string describing the entire chart

        """
        plots_text = PlotsText(plots_data=plots_data)
        return plots_text.construct_text()

    def generate_chart_output(self) -> ChartOutput:
        """Generates a `plotly` chart figure and a corresponding description

        Returns:
            An enriched `ChartOutput` model containing:
                figure - a plotly `Figure` object for the created chart
                    description - a string representation
                    which summarises the produced chart
        """
        chart_generation_payload: ChartGenerationPayload = (
            self._build_chart_generation_payload()
        )
        description = self.build_chart_description(
            plots_data=chart_generation_payload.plots
        )
        figure = self._build_chart_figure(
            chart_generation_payload=chart_generation_payload
        )

        return ChartOutput(
            figure=figure,
            description=description,
            is_headline=self.is_headline_data,
        )
