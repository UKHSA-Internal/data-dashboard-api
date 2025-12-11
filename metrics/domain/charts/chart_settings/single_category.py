import datetime
import logging
from decimal import Decimal

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.base import ChartSettings
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.charts.utils import (
    return_formatted_max_y_axis_value,
    return_formatted_min_y_axis_value,
)
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


class SingleCategoryChartSettings(ChartSettings):
    def __init__(self, *, chart_generation_payload: ChartGenerationPayload):
        super().__init__(chart_generation_payload=chart_generation_payload)
        self.plots_data: list[PlotGenerationData] = chart_generation_payload.plots

    @property
    def is_date_type_x_axis(self) -> bool:
        return isinstance(self.plots_data[0].x_axis_values[0], datetime.date)

    def _get_x_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
        tick_font = self._get_tick_font_config()
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
            "tickfont": self._get_tick_font_config(),
            "autotickangles": [0, 90],
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

    def _get_y_axis_config(self) -> dict[str, bool | DICT_OF_STR_ONLY]:
        tick_font = self._get_tick_font_config()
        base_y_axis_config = {
            "ticks": "outside",
            "tickson": "boundaries",
            "tickcolor": "rgba(0,0,0,0)",
            "tickformatstops": [
                {"dtickrange": [None, 999], "value": ","},
                {"dtickrange": [1000, 99999], "value": ",.0f"},
                {"dtickrange": [100000, None], "value": ".0s"},
            ],
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

        y_min_value, y_max_value = self._get_minimum_and_maximum_y_axis_values()

        base_y_axis_config["tick0"] = y_min_value

        if self.y_axis_maximum_value:
            base_y_axis_config["range"] = [y_min_value, y_max_value]

        base_y_axis_config["rangemode"] = "tozero" if y_min_value == 0 else "normal"

        return base_y_axis_config

    def _get_minimum_and_maximum_y_axis_values(self) -> list[Decimal]:
        """Returns the y-axis minimum and maximum value, which can be either a manual
        value provided in a request or the minimum and maximum value

        Notes:
            if a `y_axis_minimum_value` is provided that is higher than the
            lowest value in the `y_axis_values` list then the min value of
            `y_axis_values` is used as the lowest number in the y-axis range.

            if a `y_axis_maximum_value` is provided that is lower than the
            highest value in the `y_axis_values` list then the max value of
            `y_axis_values` is used as the highest number in the y-axis range.

        Returns:
            A list containing two values the minimum y-axis value
            and the maximum y-axis value
        """
        y_axis_range = [item for row in self.plots_data for item in row.y_axis_values]

        if self.y_axis_minimum_value < min(y_axis_range):
            min_value = self.y_axis_minimum_value
        else:
            min_value = min(y_axis_range)

        if self.y_axis_maximum_value and (
            self.y_axis_maximum_value > max(y_axis_range)
        ):
            max_value = self.y_axis_maximum_value
        else:
            max_value = max(y_axis_range)

        return [min_value, max_value]

    @staticmethod
    def get_x_axis_text_type() -> DICT_OF_STR_ONLY:
        return {
            "type": "-",
            "dtick": None,
            "tickformat": None,
        }

    def _get_legend_top_centre_config(self):
        legend_config = {
            "font": self._get_tick_font_config(),
            "orientation": "h",
            "y": 1.0,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "bottom",
        }

        if legend_title := self._chart_generation_payload.legend_title:
            legend_config["title"] = f"<b>{legend_title}</b>"

        return {
            "legend": legend_config,
        }

    def _get_min_and_max_x_axis_values(self) -> tuple[str, str]:
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

    @staticmethod
    def get_timeseries_margin_days(interval: str | int) -> int:
        """Returns a number of days as an integer based on the provided interval.

        Note:
            This value is used to shift the start and end date on timeseries charts
            to avoid cropping issues with Plotly by padding out the timeframe of a chart.

            The interval, which is used for `dtick` attribute of a chart can be either
            a `str` or `int` this is because while we use the D3 time interval convention
            of `M1`, `M3`, `M12` etc. for weekly and fortnightly intervals
            milliseconds are used due to a lack of support for these intervals in string
            format.

        Returns:
            number of days as an integer
        """
        if interval == "M1":
            return 15
        if interval == "M3":
            return 45
        if interval == "M6":
            return 90
        if interval == "M12":
            return 178
        return 1

    def get_x_axis_range(
        self, min_date: int, max_date: int, interval: str | int
    ) -> list[datetime.date]:
        """Returns the first and last date to make up the timeseries date range.

        Note:
            Plotly can sometimes crop or partially hide the first and last data points
            in charts. To prevent this rendering issue, we adjust the date range:
            - Shift the first date backwards by half the current time interval
            - Shift the last date forwards by half the current time interval
            - If timeseries intervals are less than 1 month we shift the dates by 1 day

            Eg:
            - For 1-year interval, 178 days (just under 6 months)
            - For 6-month interval, shift by 90 days
            - For 1-month interval, shift by 1 day

            This ensures all data points are fully visible and not cut off at the
            chart's edges.

        Returns:
            A list containing two dates, the first in the timeseries and the last `list[datetime.date]`
        """
        return [
            (
                min_date
                - datetime.timedelta(
                    days=self.get_timeseries_margin_days(interval=interval)
                )
            ),
            (
                max_date
                + datetime.timedelta(
                    days=self.get_timeseries_margin_days(interval=interval)
                )
            ),
        ]

    def get_x_axis_date_type(self) -> DICT_OF_STR_ONLY:
        min_date, max_date = self._get_min_and_max_x_axis_values()

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
            "range": self.get_x_axis_range(
                min_date=tick0, max_date=max_date, interval=dtick
            ),
        }

    def _build_line_single_simplified_y_axis_value_params(
        self,
    ) -> dict[str, list[str | int | Decimal]]:
        """Returns a dictionary containing `y-axis` parameter values

        Returns:
            A dictionary containing the y-axis parameters than make up the
            y-axis ticks and tick values.
        """
        min_value, max_value = self._get_minimum_and_maximum_y_axis_values()

        return {
            "y_axis_tick_values": [min_value, max_value],
            "y_axis_tick_text": [
                return_formatted_min_y_axis_value(y_axis_values=[min_value]),
                return_formatted_max_y_axis_value(y_axis_values=[max_value]),
            ],
            "range": [min_value, max_value],
        }

    def _build_line_single_simplified_axis_params(
        self,
    ) -> dict[str, list[str | int | Decimal]]:
        """Creates the parameters for `get_line_single_simplified_chart_config`

        Returns:
            dictionary of parameters for charts settings parameters
        """
        plot_data = self.plots_data[0]

        y_axis_params = self._build_line_single_simplified_y_axis_value_params()

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
        axis_params = self._build_line_single_simplified_axis_params()

        # Chart Config
        chart_config = self._get_base_chart_config()
        chart_config["showlegend"] = False
        chart_config["margin"]["r"] = 35
        chart_config["margin"]["l"] = 25
        chart_config["margin"]["t"] = 12
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

    def get_line_multi_coloured_chart_config(self):
        chart_config = self._get_base_chart_config()

        return {**chart_config, **self._get_legend_top_centre_config()}

    def get_common_chart_config(self):
        chart_config = self._get_base_chart_config()

        chart_config["barmode"] = "group"
        return {**chart_config, **self._get_legend_top_centre_config()}


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
