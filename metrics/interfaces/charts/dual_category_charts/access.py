import io
import urllib.parse
from datetime import datetime

import plotly.graph_objects as go
from django.db.models import Manager
from scour import scour

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
#from metrics.domain.charts import ()
from metrics.domain.common.utils import (
    ChartTypes,
    extract_metric_group_from_metric,
)
from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams
)
# from metrics.domain.models import (
#     ChartGenerationPayload,
#     ChartRequestParams,
#     PlotGenerationData,
# )
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
        chart_reqeust_params: DualCategoryChartRequestParams,
        core_model_manager:  CORE_MODEL_MANAGER_TYPE = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: PlotsInterface | None = None,
    ):
        self.chart_reqeust_params = chart_reqeust_params
        self.chart_type = self.chart_reqeust_params.chart_type
        self.metric_group = extract_metric_group_from_metric(
            metric=self.chart_reqeust_params.static_fields.metric,
        )
        self.core_model_manager = core_model_manager
        self.plots_interface = plots_interface or PlotsInterface(
            chart_request_params=self.chart_reqeust_params,
            core_model_manager=self.core_model_manager,
        )

        self._latest_date: str = ""

    @property
    def in_headline_data(self) -> bool:
        return self.chart_reqeust_params.plots[0].is_headline_data


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
            return DEFAULT_CORE_TIME_SERIES_MANAGER

        return DEFAULT_CORE_HEADLINE_MANAGER


    def generate_chart_output(self) -> ChartOutput:
        pass

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
    charts_interface = DualCategoryChartsInterface(chart_reqeust_params=chart_request_params)
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return charts_interface.write_figure(figure=chart_output.figure)