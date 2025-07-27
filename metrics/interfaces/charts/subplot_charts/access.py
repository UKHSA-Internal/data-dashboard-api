from typing import Any
from dataclasses import dataclass

import plotly.graph_objects

from django.db.models.manager import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import ChartGenerationPayload
from metrics.domain.models.charts.subplot_charts import (
    SubplotChartRequestParameters,
)
from metrics.domain.models.subplot_plots import (
    SubplotChartRequestParams,
    SubplotChartSubplotData
)
from metrics.interfaces.subplots.access import SubplotsInterface

DEFAULT_SUBPLOT_CHART_TYPE = "bar"

@dataclass
class ChartOutput:
    figure: plotly.graph_objects.Figure
    description: str


class ChartsInterface:
    def __init__(
        self,
        *,
        chart_request_params: SubplotChartRequestParameters,
        core_time_series_manager: type[Manager] = CoreTimeSeries.objects,
    ):
        """
        WIP: for now we'll integrate with time_series model_manager only
             as we'll assume bar chart for the type (this is for cover).
        """
        self.chart_request_params = chart_request_params
        self.chart_type = DEFAULT_SUBPLOT_CHART_TYPE
        self.subplot_interface = SubplotsInterface(
            chart_request_params=chart_request_params,
        )

    def _build_chart_generation_payload(self) -> SubplotChartRequestParams:
        subplot_data: list[SubplotChartSubplotData] = (
            self.subplot_interface.build_subplots_data()
        )
        return SubplotChartRequestParams(
            subplot_data=subplot_data,
            chart_width=self.chart_request_params.chart_width,
            chart_height=self.chart_request_params.chart_height,
            x_axis_title=self.chart_request_params.x_axis_title,
            y_axis_title=self.chart_request_params.y_axis_title,
            y_axis_minimum_value=self.chart_request_params.y_axis_minimum_value,
            y_axis_maximum_value=self.chart_request_params.y_axis_maximum_value,
        )

    @staticmethod
    def _build_chart_figure(
        chart_generation_payload: SubplotChartRequestParams
    ) -> plotly.graph_objects.Figure:
        return {}

    def generate_chart_output(self):
        """Generates a `plotly` chart figure and a corresponding description

        Returns:
            An enriched `ChartOutput` model containing:
            figure of the created chart and description to summarise
            the produced chart
        """
        chart_generation_payload: SubplotChartRequestParams = (
            self._build_chart_generation_payload()
        )

        figure = self._build_chart_figure(
            chart_generation_payload=chart_generation_payload,
        )

        # Temporary chart description - following ticket to implement
        chart_description = "Subplot chart comparing multiple metrics"

        return ChartOutput(
            figure=figure,
            description=chart_description,
        )

def generate_chart_file(
    *, chart_request_params: SubplotChartRequestParameters
) -> bytes:
    charts_interface = ChartsInterface(chart_request_params=chart_request_params)
    chart_output = charts_interface.generate_chart_output()

    # return charts_interface.write_figure()
