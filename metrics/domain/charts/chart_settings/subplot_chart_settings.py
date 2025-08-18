import logging
import math

from metrics.domain.charts.chart_settings.base import ChartSettings
from metrics.domain.charts.type_hints import CHART_ARGS
from metrics.domain.models import SubplotGenerationData
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload

logger = logging.getLogger(__name__)

DEFAULT_LEGEND_FONT_SIZE = 14


class SubplotChartSettings(ChartSettings):

    def __init__(self, *, chart_generation_payload: SubplotChartGenerationPayload):
        super().__init__(chart_generation_payload=chart_generation_payload)
        self.subplot_data: SubplotGenerationData = chart_generation_payload.subplot_data

    def _get_x_axis_config(self) -> CHART_ARGS:
        return {
            "showgrid": True,
            "griddash": "dash",
            "gridcolor": "rgba(200,200,200,0.5)",
            "ticklen": 5,
            "ticks": "outside",
            "tickfont": self._get_tick_font_config(),
        }

    def _get_y_axis_config(self) -> CHART_ARGS:
        return {
            "showticklabels": False,
            "ticklen": 0,
            "ticks": "outside",
            "tickfont": self._get_tick_font_config(),
            "tickson": "boundaries",
            "showgrid": True,
            "gridcolor": "rgba(220, 220, 220, 0.7)",
            "griddash": "dash",
        }

    @staticmethod
    def get_make_subplots_config() -> CHART_ARGS:
        return {
            "rows": 1,
            "shared_xaxes": True,
            "shared_yaxes": True,
            "horizontal_spacing": 0.03,
        }

    def get_legend_bottom_centre_config(self, number_of_legend_items: int):
        y_base = 0.2
        y_multiplier = math.ceil(number_of_legend_items / 4)

        return {
            "font": {**self._get_tick_font_config(), "size": DEFAULT_LEGEND_FONT_SIZE},
            "orientation": "h",
            "y": -(y_base * y_multiplier),
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "bottom",
        }

    def get_subplot_chart_config(self, number_of_legend_items: int) -> CHART_ARGS:
        chart_config = self._get_base_chart_config()

        chart_config["legend"] = self.get_legend_bottom_centre_config(
            number_of_legend_items=number_of_legend_items
        )
        chart_config["autosize"] = True
        chart_config["margin"] = {
            "l": 3,
            "b": 3,
            "t": 3,
        }

        return chart_config

    def get_subplot_xaxis_config(self) -> CHART_ARGS:
        yaxis_config = self._get_x_axis_config()

        yaxis_config["row"] = 1

        return yaxis_config

    def get_subplot_yaxis_config(self) -> CHART_ARGS:
        yaxis_config = self._get_y_axis_config()

        yaxis_config["row"] = 1

        return yaxis_config

    def get_primary_subplot_yaxis_config(self) -> CHART_ARGS:
        primary_yaxis_config = self._get_y_axis_config()

        primary_yaxis_config["row"] = 1
        primary_yaxis_config["col"] = 1
        primary_yaxis_config["showticklabels"] = True
        primary_yaxis_config["ticklen"] = 5

        return primary_yaxis_config
