import datetime
import logging
from decimal import Decimal

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.charts.utils import (
    return_formatted_max_y_axis_value,
    return_formatted_min_y_axis_value,
)
from metrics.domain.common.utils import DEFAULT_CHART_WIDTH
from metrics.domain.models import PlotGenerationData
from metrics.domain.models.plots import ChartGenerationPayload

logger = logging.getLogger(__name__)

SEVEN_DAYS = 7
SIXTY_ONE_DAYS = 61
NINTY_TWO_DAYS = 92
TWELVE_MONTHS = 12
TWENTY_FOUR_MONTHS = 24
THIRTY_SIX_MONTHS = 36
WEEK_IN_MILLISECONDS = 604800000
TWO_WEEKS_IN_MILLISECONDS = 1209600000


class ChartSettings:
    narrow_chart_width = DEFAULT_CHART_WIDTH

    def __init__(self, *, chart_generation_payload: ChartGenerationPayload):
        self._chart_generation_payload = chart_generation_payload
        self.plots_data: list[PlotGenerationData] = chart_generation_payload.plots

    @property
    def width(self) -> int:
        return self._chart_generation_payload.chart_width

    @property
    def height(self) -> int:
        return self._chart_generation_payload.chart_height

    @property
    def y_axis_minimum_value(self) -> int | Decimal:
        return self._chart_generation_payload.y_axis_minimum_value

    @property
    def y_axis_maximum_value(self) -> int | Decimal | None:
        return self._chart_generation_payload.y_axis_maximum_value

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
        tick_font = self.get_tick_font_config()
        base_x_axis_config = {
            "showspikes": True,
            "spikecolor": "#b1b4b6",
            "spikedash": "2px",
            "spikethickness": 1,
            "spikemode": "toaxis+across+marker",
            "spikesnap": "cursor",
            "showgrid": True,
            "showline": False,
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

        if self._chart_generation_payload.x_axis_title:
            base_x_axis_config["title"] = {
                "text": self._chart_generation_payload.x_axis_title,
                "font": tick_font,
            }

        x_axis_type_config = (
            self.get_x_axis_date_type()
            if self.is_date_type_x_axis
            else self.get_x_axis_text_type()
        )

        return {**base_x_axis_config, **x_axis_type_config}

    def get_y_axis_config(self) -> dict[str, bool | DICT_OF_STR_ONLY]:
        tick_font = self.get_tick_font_config()
        base_y_axis_config = {
            "ticks": "outside",
            "tickson": "boundaries",
            "tickcolor": "rgba(0,0,0,0)",
            "showgrid": False,
            "showticklabels": True,
            "fixedrange": True,
            "gridcolor": "#000",
            "tickfont": tick_font,
            "rangemode": "tozero",
        }

        if self._chart_generation_payload.y_axis_title:
            base_y_axis_config["title"] = {
                "text": self._chart_generation_payload.y_axis_title,
                "font": tick_font,
            }

        return base_y_axis_config

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

    def build_line_single_simplified_y_axis_value_params(
        self,
    ) -> dict[str, list[str | int | Decimal]]:
        """Returns a dictionary containing `y-axis` parameter values

        Notes:
            if a `y_axis_minimum_value` is provided that is higher than the
            lowest value in the `y_axis_values` list then the min value of
            `y_axis_values` is used as the lowest number in the y-axis range.

            if a `y_axis_maximum_value` is provided that is lower than the
            highest value in the `y_axis_values` list then the max value of
            `y_axis_values` is used as the highest number in the y-axis range.

        Returns:
            A dictionary containing the y-axis parameters than make up the
            y-axis ticks and tick values.
        """
        plots_data = self.plots_data[0]

        if self.y_axis_minimum_value < min(plots_data.y_axis_values):
            min_value = self.y_axis_minimum_value
        else:
            min_value = min(plots_data.y_axis_values)
            logger.info(
                "The minimum value provided was to high, fallen back to the min value in the data"
            )

        if self.y_axis_maximum_value and (
            self.y_axis_maximum_value > max(plots_data.y_axis_values)
        ):
            max_value = self.y_axis_maximum_value
        else:
            max_value = max(plots_data.y_axis_values)
            logger.info(
                "The maximum value provided was to low, fallen back to the max value in the data"
            )

        return {
            "y_axis_tick_values": [min_value, max_value],
            "y_axis_tick_text": [
                return_formatted_min_y_axis_value(y_axis_values=[min_value]),
                return_formatted_max_y_axis_value(y_axis_values=[max_value]),
            ],
            "range": [min_value, max_value],
        }

    def build_line_single_simplified_axis_params(
        self,
    ) -> dict[str, list[str | int | Decimal]]:
        """Creates the parameters for `get_line_single_simplified_chart_config`

        Returns:
            dictionary of parameters for charts settings parameters
        """
        plot_data = self.plots_data[0]

        y_axis_params = self.build_line_single_simplified_y_axis_value_params()

        return {
            "x_axis_tick_values": [
                plot_data.x_axis_values[0],
                plot_data.x_axis_values[-1],
            ],
            "x_axis_tick_text": [
                plot_data.x_axis_values[0].strftime("%b, %Y"),
                plot_data.x_axis_values[-1].strftime("%b, %Y"),
            ],
            "y_axis_tick_values": y_axis_params["y_axis_tick_values"],
            "y_axis_tick_text": y_axis_params["y_axis_tick_text"],
            "range": y_axis_params["range"],
            "rangemode": (
                "tozero" if y_axis_params["y_axis_tick_values"][0] == 0 else "normal"
            ),
        }

    def get_line_single_simplified_chart_config(self):

        axis_params = self.build_line_single_simplified_axis_params()

        # Chart Config
        chart_config = self.get_base_chart_config()
        chart_config["showlegend"] = False
        chart_config["margin"]["r"] = 35
        chart_config["margin"]["l"] = 25
        chart_config["margin"]["pad"] = 25

        # x_axis config
        chart_config["xaxis"]["showgrid"] = False
        chart_config["xaxis"]["ticks"] = "outside"
        chart_config["xaxis"]["tickvals"] = axis_params["x_axis_tick_values"]
        chart_config["xaxis"]["ticktext"] = axis_params["x_axis_tick_text"]
        chart_config["xaxis"]["ticklen"] = 0
        chart_config["xaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified

        # y_axis config
        chart_config["yaxis"]["zeroline"] = False
        chart_config["yaxis"]["ticks"] = "outside"
        chart_config["yaxis"]["tickvals"] = axis_params["y_axis_tick_values"]
        chart_config["yaxis"]["ticktext"] = axis_params["y_axis_tick_text"]
        chart_config["yaxis"]["ticklen"] = 0
        chart_config["yaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified
        chart_config["yaxis"]["range"] = axis_params["range"]
        chart_config["yaxis"]["rangemode"] = axis_params["rangemode"]

        return chart_config

    def get_bar_chart_config(self):
        chart_config = self.get_base_chart_config()
        chart_config["barmode"] = "group"
        return {**chart_config, **self._get_legend_bottom_left_config()}

    def get_line_multi_coloured_chart_config(self):
        chart_config = self.get_base_chart_config()
        return {**chart_config, **self._get_legend_top_centre_config()}

    def _get_date_tick_format(self, *, weekly: bool = False) -> str:
        if weekly:
            return "%d %b<br>%Y"

        return "%b %Y" if self.width > self.narrow_chart_width else "%b<br>%Y"

    def get_min_and_max_x_axis_values(self) -> tuple[str, str]:
        possible_minimums = []
        possible_maximums = []

        for plot_data in self.plots_data:
            possible_minimums.append(plot_data.x_axis_values[0])
            possible_maximums.append(plot_data.x_axis_values[-1])

        return min(possible_minimums), max(possible_maximums)

    @staticmethod
    def get_x_axis_interval(days: int, months: int) -> str | int:
        """Returns the `dtick` used for date intervals based on the number
        of days and months in the current date range.

        Note:
            for weekly and `fortnightly` milliseconds were used due to a lack of support
            for these intervals using a string format such as `M1` for monthly
            604800000 = weekly
            1209600000 = fortnightly

        Args:
            days: Integer representing the number of days
            months: Integer representing the number of months

        Returns: list of strings | int containing the `dtick` value
        """
        if days <= SEVEN_DAYS:
            return "D7"
        if days <= SIXTY_ONE_DAYS:
            return WEEK_IN_MILLISECONDS
        if days <= NINTY_TWO_DAYS:
            return TWO_WEEKS_IN_MILLISECONDS
        if months <= TWELVE_MONTHS:
            return "M1"
        if months <= TWENTY_FOUR_MONTHS:
            return "M3"
        if months <= THIRTY_SIX_MONTHS:
            return "M6"
        return "M12"

    def get_x_axis_date_type(self) -> DICT_OF_STR_ONLY:
        min_date, max_date = self.get_min_and_max_x_axis_values()

        number_of_days, number_of_months = get_number_of_days_and_months(
            min_date=min_date, max_date=max_date
        )

        tick0 = min_date.replace(day=1)

        dtick = self.get_x_axis_interval(
            days=number_of_days,
            months=number_of_months,
        )

        weekly = number_of_days <= NINTY_TWO_DAYS

        return {
            "type": "date",
            "tick0": tick0,
            "dtick": dtick,
            "tickformat": self._get_date_tick_format(weekly=weekly),
            "range": [tick0, max_date],
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


def get_number_of_days_and_months(
    min_date: datetime.date, max_date: datetime.date
) -> list[int]:
    """Takes two datetime.date objects and returns the number of days and months in the time frame.

    Args:
        min_date: represents the earliest date in the time series, this is the first day of the
            earliest month. Eg: '2025-01-27' will have a `min_date` of '2025-01-01'
        max_date: The last day in the time series Eg '2025-01-15' will be '2025-01-15'

    Returns:
        A list of 2 integers representing the number of days and months between the two dates provided.
    """
    number_of_days = (max_date - min_date).days
    number_of_months = (max_date.year - min_date.year) * 12 + (
        max_date.month - min_date.month
    )
    return [number_of_days, number_of_months]
