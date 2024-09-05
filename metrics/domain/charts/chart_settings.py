import datetime

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.common.utils import DEFAULT_CHART_WIDTH, get_last_day_of_month
from metrics.domain.models import PlotData


class ChartSettings:
    narrow_chart_width = DEFAULT_CHART_WIDTH

    def __init__(self, *, width: int, height: int, plots_data: list[PlotData]):
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

    @property
    def is_date_type_x_axis(self) -> bool:
        return isinstance(self.plots_data[0].x_axis_values[0], datetime.date)

    def get_x_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
        base_x_axis_config = {
            "showspikes": True,
            "spikecolor": "#b1b4b6",
            "spikedash": "2px",
            "spikethickness": 1,
            "spikemode": "toaxis+across+marker",
            "spikesnap": "cursor",
            "showgrid": True,
            "zeroline": False,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "date",
            "tickcolor": "rgba(0,0,0,0)",
            "dtick": "M1",
            "tickformat": "%b %Y",
            "tickfont": self.get_tick_font_config(),
        }

        x_axis_type_config = (
            self.get_x_axis_date_type()
            if self.is_date_type_x_axis
            else self.get_x_axis_text_type()
        )

        return {**base_x_axis_config, **x_axis_type_config}

    def get_y_axis_config(self) -> dict[str, bool | DICT_OF_STR_ONLY]:
        return {
            "showgrid": False,
            "showticklabels": True,
            "fixedrange": True,
            "gridcolor": "#000",
            "tickfont": self.get_tick_font_config(),
        }

    def get_base_chart_config(self):
        return {
            "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "hoverlabel": {
                "align": "left",
                "bgcolor": "white",
            },
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
            "showlegend": True,
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
        min_date, max_date = self.get_min_and_max_x_axis_values()
        max_date = get_max_date_for_current_month(existing_dt=max_date)

        return {
            "type": "date",
            "dtick": "M1",
            "tickformat": self._get_date_tick_format(),
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


def get_max_date_for_current_month(
    *,
    existing_dt: str | datetime.datetime | datetime.date,
) -> datetime.date:
    """Returns the 15th of the given `existing_dt` or the last day of the month

    Args:
        existing_dt: The date we want to get the max date for

    Returns:
        The max allowable date for the current month

    """
    existing_dt = str(existing_dt)
    try:
        datestamp, _ = existing_dt.split()
    except ValueError:
        # Thrown when a date i.e. `2024-02-15` is provided
        # instead of a datetime i.e. `2024-02-15 13:52:00`
        datestamp = existing_dt

    year, month, day = map(int, datestamp.split("-"))

    middle_of_month = 15
    if day <= middle_of_month:
        return datetime.date(year=year, month=month, day=middle_of_month)
    return get_last_day_of_month(date=datetime.date(year=year, month=month, day=day))
