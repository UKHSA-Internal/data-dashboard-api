from typing import Any, Dict, List, Union

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.models import PlotsData


class ChartSettings:
    narrow_chart_width = 435

    def __init__(self, width: int, height: int, plots_data: PlotsData):
        self._width = width
        self._height = height
        self.plots_data = plots_data

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @staticmethod
    def get_tick_font_config() -> DICT_OF_STR_ONLY:
        return {
            "family": "Arial",
            "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
        }

    def get_x_axis_config(self) -> Dict[str, Union[str, bool, DICT_OF_STR_ONLY]]:
        return {
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b %Y",
            "tickfont": self.get_tick_font_config(),
        }

    def get_y_axis_config(self) -> Dict[str, Union[bool, DICT_OF_STR_ONLY]]:
        return {
            "showgrid": False,
            "showticklabels": False,
            "tickfont": self.get_tick_font_config(),
        }

    def get_base_chart_config(self):
        return {
            "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "margin": {
                "l": 0,
                "r": 0,
                "b": 0,
                "t": 0,
            },
            "autosize": False,
            "xaxis": self.get_x_axis_config(),
            "yaxis": self.get_y_axis_config(),
            "height": self.height,
            "width": self.width,
        }

    def get_simple_line_chart_config(self) -> Dict[str, Dict[str, bool]]:
        set_axes_to_be_invisible = {"visible": False}
        return {
            "xaxis": set_axes_to_be_invisible,
            "yaxis": set_axes_to_be_invisible,
            "plot_bgcolor": colour_scheme.RGBAColours.LINE_LIGHT_GREY.stringified,
            "width": self.width,
            "height": self.height,
        }

    def get_waffle_chart_config(self):
        x_axis_args = {
            "showgrid": False,
            "ticks": None,
            "showticklabels": False,
        }
        y_axis_args = {
            **x_axis_args,
            **{"scaleratio": 1, "scaleanchor": "x"},
        }
        return {
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "showlegend": False,
            "plot_bgcolor": colour_scheme.RGBAColours.LIGHT_GREY.stringified,
            "paper_bgcolor": colour_scheme.RGBAColours.WAFFLE_WHITE.stringified,
            "xaxis": x_axis_args,
            "yaxis": y_axis_args,
            "width": self.width,
            "height": self.height,
        }

    def get_line_with_shaded_section_chart_config(self):
        chart_config = self.get_base_chart_config()
        chart_config["showlegend"] = False
        return chart_config

    def _get_x_axis_date_type(self) -> DICT_OF_STR_ONLY:
        tick_format = "%b %Y" if self.width > self.narrow_chart_width else "%b<br>%Y"
        return {
            "type": "date",
            "dtick": "M1",
            "tickformat": tick_format,
        }

    @staticmethod
    def _get_x_axis_text_type() -> DICT_OF_STR_ONLY:
        return {
            "type": "-",
            "dtick": None,
            "tickformat": None,
        }
