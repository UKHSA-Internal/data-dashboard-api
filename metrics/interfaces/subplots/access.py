from metrics.domain.models.subplot_plots import SubplotChartRequestParams


class SubplotsInterface:
    def __init__(
        self,
        *,
        chart_request_params: SubplotChartRequestParams,
        core_time_series_manager: type[Manager] = CoreTimeSeries.objects,
    ):
        """
        WIP: ...
        """
        self.chart_request_params = chart_request_params
        self.time_series_manager = core_time_series_manager

    def _build_chart_subplots_data(self) -> list[str]:
        """Creates a list of `SubplotData`"""
        pass