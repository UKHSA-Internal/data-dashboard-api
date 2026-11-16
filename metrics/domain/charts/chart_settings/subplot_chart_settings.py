import logging

from metrics.domain.charts.chart_settings.base import ChartSettings
from metrics.domain.charts.type_hints import CHART_ARGS
from metrics.domain.models import SubplotGenerationData
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload

logger = logging.getLogger(__name__)

DEFAULT_LEGEND_FONT_SIZE = 14
DEFAULT_ANNOTATION_FONT_SIZE = 14

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

    def _get_margin_top_px(self) -> int:
        return 30 if self._chart_generation_payload.y_axis_title else 3

    def _get_approx_plot_height_px(self) -> int:
        return max(self.height - self._get_margin_top_px() - 88, 50)

    def _has_x_axis_title(self) -> bool:
        return bool(self._chart_generation_payload.x_axis_title)

    def _get_xaxis_title_offset_px(self) -> int:
        """More space needed for x-axis title when present"""
        return 30 if self._has_x_axis_title() else 0

    def _get_legend_top_offset_px(self) -> int:
        """Distance from the x-axis line to the top edge of the legend"""
        return (
                self._get_xaxis_title_offset_px()
                + (
                    40
                    if self._has_x_axis_title()
                    else 50
                )
        )

    def get_legend_config(self) -> CHART_ARGS:
        legend_top_offset_px = self._get_legend_top_offset_px()

        return {
            "font": {**self._get_tick_font_config(), "size": DEFAULT_LEGEND_FONT_SIZE},
            "orientation": "h",
            "yref": "paper",
            "y": -legend_top_offset_px / self._get_approx_plot_height_px(),
            "yanchor": "top",
            "x": 0.5,
            "xanchor": "center",
        }

    def get_subplot_chart_config(self) -> CHART_ARGS:
        chart_config = self._get_base_chart_config()

        chart_config["legend"] = self.get_legend_config()
        chart_config["autosize"] = True
        chart_config["margin"] = {
            "l": 3,
            "b": 3,
            "t": self._get_margin_top_px(),
        }

        return chart_config

    def get_subplot_xaxis_config(self) -> CHART_ARGS:
        x_axis_config = self._get_x_axis_config()
        x_axis_config["row"] = 1
        return x_axis_config

    def get_subplot_yaxis_config(self) -> CHART_ARGS:
        y_axis_config = self._get_y_axis_config()
        y_axis_config["row"] = 1

        return y_axis_config

    def get_primary_subplot_yaxis_config(self) -> CHART_ARGS:
        primary_yaxis_config = self._get_y_axis_config()

        primary_yaxis_config["row"] = 1
        primary_yaxis_config["col"] = 1
        primary_yaxis_config["showticklabels"] = True
        primary_yaxis_config["ticklen"] = 5

        return primary_yaxis_config

    def get_x_axis_title_as_annotation_config(self) -> dict:
        annotations = list(self._get_y_axis_title_annotation_config() or [])

        annotations.append(
            {
                "text": self._chart_generation_payload.x_axis_title,
                "x": 0.5,
                "y": -75 / self._get_approx_plot_height_px(),
                "xanchor": "center",
                "yanchor": "bottom",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    **self._get_tick_font_config(),
                    "size": DEFAULT_ANNOTATION_FONT_SIZE,
                },
            }
        )

        return {"annotations": annotations}