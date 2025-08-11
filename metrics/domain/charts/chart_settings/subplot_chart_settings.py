import logging

from metrics.domain.charts.chart_settings.base import ChartSettings
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.models import SubplotGenerationData
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload

logger = logging.getLogger(__name__)

# create a base config for subplots
#


class SubplotChartSettings(ChartSettings):

    def __init__(self, *, chart_generation_payload: SubplotChartGenerationPayload):
        super().__init__(chart_generation_payload=chart_generation_payload)
        self.subplot_data: SubplotGenerationData = chart_generation_payload.subplot_data

    def _get_x_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
        pass

    def _get_y_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
        pass

    def get_subplot_chart_config(self):
        chart_config = self._get_base_chart_config()

        chart_config["barmode"] = "group"
        return {**chart_config}
