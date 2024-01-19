from datetime import datetime

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.line_multi_coloured.properties import is_legend_required
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.models import PlotData
from metrics.domain.utils import DEFAULT_CHART_WIDTH, get_last_day_of_month


class ChartSettings:
    narrow_chart_width = DEFAULT_CHART_WIDTH

    def __init__(self, width: int, height: int, plots_data: list[PlotData]):
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

    def get_x_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
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

    def get_y_axis_config(self) -> dict[str, bool | DICT_OF_STR_ONLY]:
        return {
            "showgrid": False,
            "showticklabels": True,
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

    def get_simple_line_chart_config(self) -> dict[str, dict[str, bool]]:
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
        y_axis_args = x_axis_args | {"scaleratio": 1, "scaleanchor": "x"}

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

    def get_bar_chart_config(self):
        chart_config = self.get_base_chart_config()
        chart_config["barmode"] = "group"
        return {**chart_config, **self._get_legend_bottom_left_config()}

    def get_line_multi_coloured_chart_config(self):
        chart_config = self.get_base_chart_config()
        chart_config["showlegend"] = is_legend_required(
            chart_plots_data=self.plots_data
        )
        return {**chart_config, **self._get_legend_top_centre_config()}

    def _get_date_tick_format(self) -> str:
        return "%b %Y" if self.width > self.narrow_chart_width else "%b<br>%Y"

    def get_min_and_max_x_axis_values(self) -> tuple[str, str]:
        possible_minimums = []
        possible_maximums = []

        for plot_data in self.plots_data:
            possible_minimums.append(plot_data.x_axis_values[0])
            possible_maximums.append(plot_data.x_axis_values[-1])

        return min(possible_minimums), max(possible_maximums)

    def get_x_axis_date_type(self) -> DICT_OF_STR_ONLY:
        tick_format = self._get_date_tick_format()

        min_date, max_date = self.get_min_and_max_x_axis_values()
        max_date = get_new_max_date(existing_dt=max_date)

        return {
            "type": "date",
            "dtick": "M1",
            "tickformat": tick_format,
            "range": [min_date, max_date],
        }

    @staticmethod
    def get_x_axis_text_type() -> DICT_OF_STR_ONLY:
        return {
            "type": "-",
            "dtick": None,
            "tickformat": None,
        }

    @staticmethod
    def get_margin_for_charts_with_dates():
        return {
            "margin": {
                "l": 15,
                "r": 15,
                "b": 0,
                "t": 0,
            }
        }

    @staticmethod
    def _get_legend_bottom_left_config():
        return {
            "legend": {
                "orientation": "h",
                "y": -0.25,
                "x": 0,
            },
        }

    @staticmethod
    def _get_legend_top_centre_config():
        return {
            "legend": {
                "orientation": "h",
                "y": 1.0,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "bottom",
            },
        }


def get_new_max_date(existing_dt: str | datetime) -> str:
    """Return the last day of the month for the supplied date

    Args:
        existing_dt: The date we want the last day of the month for

    Returns:
        The last day of the month for the given date
    """
    existing_dt = str(existing_dt)
    new_date: datetime.date = get_last_day_of_month(
        date=datetime.strptime(existing_dt.split()[0], "%Y-%m-%d").date()
    )
    return new_date.strftime("%Y-%m-%d")
