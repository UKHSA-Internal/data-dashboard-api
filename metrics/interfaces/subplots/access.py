from math import expm1
from typing import Any
from django.db.models.manager import Manager

from metrics.data.models.core_models.timeseries import CoreTimeSeries

from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.domain.models.subplot_plots import SubplotChartRequestParams


class SubplotsInterface:
    def __init__(
        self,
        *,
        chart_request_params: SubplotChartRequestParameters,
        core_time_series_manager: type[Manager] = CoreTimeSeries.objects,
    ):
        self.chart_request_params = chart_request_params
        self.time_series_manager = core_time_series_manager


    def build_subplots_data(self) -> list[str]:
        """Creates a list of `SubplotData` models which hold the params and corresponding data for the requested subplots.

        Notes:
            Pydantic model...

        Returns:
            List[SubplotData]: A list of `SubplotData` models. for
                each of the requested subplots.

        """
        subplots_data: list[Any] = []

        for subplot in self.chart_request_params.subplots:
            try:
                subplot_data = []
            except Exception:
                continue

            subplots_data.append(subplot_data)

        return subplots_data
