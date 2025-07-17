from django.db.models.manager import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters

DEFAULT_SUBPLOT_CHART_TYPE = "bar"

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
        self.chart_types = DEFAULT_SUBPLOT_CHART_TYPE
        # self.subplot_interface = SubplotsInterface

    def build_chart_generation_payload(self):

        # Build plots_data `GenerationData`
        # What does this look like for subplot charts?
        # - ChartsGenerationPayload.subplots = list[SubplotChart]
        # - SubplotChart will have a list of plots for each subplot (subplot = chart)

        # Implement methods to build subplot generation data and chart data

        # subplot_data: list[SubplotGenerationData] self._build_chart_subplot_data()
        # return SubplotChartGenerationPayload(**properties)
        pass

    def generate_chart_output(self):
        """Generate chart output..."""

        # 1. build chart generation payload
        chart_generation_payload = (
            self.build_chart_generation_payload()
        )

        # 2. build chart description
        #    not required to generate the chart image leave to the end

        # 3. build chart figure
        #    updates the chart response for SVG with hover template details...

        pass


def generate_chart_file(*, chart_request_params: SubplotChartRequestParameters) -> bytes:
    charts_interface = ChartsInterface(chart_request_params=chart_request_params)
    #chart_output: ChartOutput = charts_interface.generate_chart_output()

    #return charts_interface.write_figure()
    pass
