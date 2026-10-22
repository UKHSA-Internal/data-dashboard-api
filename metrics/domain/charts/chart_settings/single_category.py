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

FULL_WIDTH_CHART_MINIMUM = 1100
FULL_WIDTH_X_AXIS_NTICKS = 13
COMPACT_X_AXIS_NTICKS = 5


def get_x_axis_figure_config() -> dict[str, dict[str, int]]:
    """Return the responsive x-axis settings used by interactive charts."""
    return {
        "xaxis_full": {"nticks": FULL_WIDTH_X_AXIS_NTICKS},
        "xaxis_compact": {"nticks": COMPACT_X_AXIS_NTICKS},
    }


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
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "linecolor": "rgba(0,0,0,0.05)",
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "date",
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": self._get_tick_font_config(),
            "autotickangles": [0, 90],
            "mirror": True,
            "ticklabeloverflow": "allow",
            "automargin": True,
        }

        if self.should_limit_x_axis_ticks:
            base_x_axis_config["nticks"] = self.get_x_axis_nticks()

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
            "showgrid": True,
            "showticklabels": True,
            "showline": True,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "linecolor": "rgba(0,0,0,0.05)",
            "mirror": True,
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
        y_axis_range = [
            item for row in self.plots_data for item in row.y_axis_values
        ] + [
            item
            for row in self.plots_data
            for item in row.additional_values.get("lower_confidence", [])
            if item
        ]

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

    def get_x_axis_nticks(self) -> int:
        """Return the maximum number of x-axis ticks for the chart width."""
        if self.width >= FULL_WIDTH_CHART_MINIMUM:
            return FULL_WIDTH_X_AXIS_NTICKS
        return COMPACT_X_AXIS_NTICKS

    @property
    def should_limit_x_axis_ticks(self) -> bool:
        """Return whether Plotly should limit ticks on this chart's x-axis"""
        return (
            self.is_date_type_x_axis
            and self.plots_data[0].parameters.is_timeseries_data
        )

    def get_x_axis_date_tick_format_stops(self) -> list[dict]:
        """Return date formats for Plotly's automatically selected tick intervel."""
        return [
            {"dtickrange": ["M12", None], "value": "%Y"},
            {
                "dtickrange": ["M1", "M12"],
                "value": self._get_date_tick_format(),
            },
            {
                "dtickrange": [None, "M1"],
                "value": self._get_date_tick_format(weekly=True),
            },
        ]

    def _get_single_x_axis_date(self) -> datetime.date | None:
        """Return the date when every x-axis value is the same date."""
        unique_x_axis_dates = {
            x_axis_value
            for plot_data in self.plots_data
            for x_axis_value in plot_data.x_axis_values
        }

        if len(unique_x_axis_dates) != 1:
            return None

        return next(iter(unique_x_axis_dates))
    
    def get_x_axis_date_type(self) -> DICT_OF_STR_ONLY:
        x_axis_date_config = {
            "type": "date",
            "autorange": True,
            "tickformatstops": self.get_x_axis_date_tick_format_stops(),
        }

        if single_x_axis_date := self._get_single_x_axis_date():
            x_axis_date_config.update(
                {
                    "tickmode": "array",
                    "tickvals": [single_x_axis_date],
                    "tickformat": self._get_date_tick_format(weekly=True),
                }
            )

        return x_axis_date_config

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
        chart_config["xaxis"]["showline"] = False
        chart_config["xaxis"]["mirror"] = False
        chart_config["xaxis"]["ticks"] = "outside"
        chart_config["xaxis"]["tickvals"] = axis_params["x_axis_tick_values"]
        chart_config["xaxis"]["ticktext"] = axis_params["x_axis_tick_text"]
        chart_config["xaxis"]["ticklen"] = 0
        chart_config["xaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified

        # y_axis config
        chart_config["yaxis"]["showgrid"] = False
        chart_config["yaxis"]["showline"] = False
        chart_config["yaxis"]["mirror"] = False
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
