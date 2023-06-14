from datetime import datetime
from typing import Dict, Tuple, Union

import plotly

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.models import PlotsData
from metrics.domain.utils import get_last_day_of_month

MARGINS_FOR_CHART_WITH_DATES = {
    "margin": {
        "l": 15,
        "r": 15,
        "b": 0,
        "t": 0,
    }
}


class ChartSettings:
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
        }

    @staticmethod
    def _get_simple_line_chart_config() -> Dict[str, Dict[str, bool]]:
        set_axes_to_be_invisible = {"visible": False}
        return {
            "xaxis": set_axes_to_be_invisible,
            "yaxis": set_axes_to_be_invisible,
            "plot_bgcolor": colour_scheme.RGBAColours.LINE_LIGHT_GREY.stringified,
        }

    def _get_waffle_chart_config(self):
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

    @staticmethod
    def _get_x_axis_date_type() -> DICT_OF_STR_ONLY:
        return {
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b %Y",
        }

    @staticmethod
    def _get_x_axis_text_type() -> DICT_OF_STR_ONLY:
        return {
            "type": "-",
            "dtick": None,
            "tickformat": None,
        }


def get_existing_chart_range(figure: plotly.graph_objs.Figure) -> Tuple[str, str]:
    """Extract the x axis range from a chart figure

    Args:
        figure: The chart figure

    Returns:
        The minimum and maximum x axis date range which Plotly has calculated
    """

    full_figure = figure.full_figure_for_development(warn=False)

    min_dt, max_dt = full_figure.layout.xaxis.range

    return min_dt, max_dt


def get_new_max_date(existing_dt: str) -> str:
    """Return the last day of the month for the supplied date

    Args:
        existing_dt: The date we want the last day of the month for

    Returns:
        The last day of the month for the given date
    """
    new_dt: datetime.date = get_last_day_of_month(
        dt=datetime.strptime(existing_dt.split()[0], "%Y-%m-%d").date()
    )
    return new_dt.strftime("%Y-%m-%d")


def get_x_axis_range(figure: plotly.graph_objs.Figure) -> Tuple[str, str]:
    """Adjust the right-hand side of the charts' x axis to give Plotly the best chance of displaying a label for every tick

    Args:
        figure: The chart figure

    Returns:
        The current minimum and the new maximum dates to use for the x axis range
        Note: If the max_date was already the last day of the month then nothing gets changed
    """

    min_date, max_dt = get_existing_chart_range(figure)

    # Go to the last day of the month to give label the best chance of being displayed
    max_date = get_new_max_date(max_dt)

    return min_date, max_date
