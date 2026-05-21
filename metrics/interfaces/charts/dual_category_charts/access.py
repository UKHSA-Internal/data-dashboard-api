import io

import plotly.graph_objects as go

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.charts.stacked_bar.generation import generate_stacked_bar

# from metrics.domain.charts import ()
from metrics.domain.common.utils import (
    extract_metric_group_from_metric,
)
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
)
from metrics.domain.models.plots import (
    ChartGenerationPayload,
    ChartRequestParams,
    PlotGenerationData,
)

# from metrics.domain.models import (
#     ChartGenerationPayload,
#     ChartRequestParams,
#     PlotGenerationData,
# )
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

        self._latest_date: str = ""

    @property
    def is_headline_data(self) -> bool:
        return self.chart_request_params.plots[0].is_headline_data

    @classmethod
    def generate_stacked_bar(cls, *, chart_generation_payload):
        """"""
        figure = generate_stacked_bar(
            chart_generation_payload=chart_generation_payload,
        )

        return figure

    def _build_chart_figure(self, *, chart_generation_payload):
        if self.chart_type == "stacked_bar":
            return self.generate_stacked_bar(
                chart_generation_payload=chart_generation_payload,
            )

    def _build_plots_data(self) -> list[PlotGenerationData]:
        plots_data: list[PlotGenerationData] = self.plots_interface.build_plots_data()

        return plots_data

    def _build_chart_generation_payload(self) -> ChartGenerationPayload:
        plots_data: list[PlotGenerationData] = self._build_plots_data()

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

    def generate_chart_output(self) -> ChartOutput:
        chart_generation_payload: ChartGenerationPayload = (
            self._build_chart_generation_payload()
        )

        figure = self._build_chart_figure(
            chart_generation_payload=chart_generation_payload
        )

        # TODO: Remove hardcoded description
        return ChartOutput(
            figure=figure,
            description="testing testing 123",
            is_headline=self.is_headline_data,
        )

    def build_chart_generation_payload(self):
        pass

    def write_figure(self, *, figure: go.Figure) -> bytes:
        """
        Convert a figure to a static image and write to a file in the desired image format

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            The image in memory

        """
        file = io.BytesIO()

        figure.write_image(
            file=file,
            format=self.chart_request_params.file_format,
            validate=False,
        )

        file.seek(0)
        return file.getvalue()


def generate_chart_as_file(*, chart_request_params: ChartRequestParams) -> str:
    charts_interface = DualCategoryChartsInterface(
        chart_request_params=chart_request_params
    )
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return charts_interface.write_figure(figure=chart_output.figure)
