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

    @staticmethod
    def build__subplots_data(self) -> list[str]:
        """Creates a list of `SubplotData` models which hold the params and corresponding data for the requested subplots.

        Notes:
            Pydantic model...

        Returns:
            List[SubplotData]: A list of `SubplotData` models. for
                each of the requested subplots.

        """
        subplot_data = []

        # process and build subplot data objects...

        return subplot_data
