import math

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.single_category import (
    SingleCategoryChartSettings,
)
from metrics.domain.models.plots import ChartGenerationPayload, PlotGenerationData

BUTTERFLY_AXIS_TICK_COUNT = 4
BUTTERFLY_AXIS_TICK_STEP_MULTIPLIERS = (1, 2, 2.5, 5, 10)
BUTTERFLY_AXIS_TICK_PRECISION = 10


def _format_axis_tick_label(*, value: float) -> str:
    """Formats the given axis tick value for display.

    Args:
        value: The value of the tick to be labelled.

    Returns:
        The value as a thousands separated string,
        with any redundant decimal place removed.
    """
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,}"


class DualCategoryChartSettings(SingleCategoryChartSettings):
    def __init__(self, *, chart_generation_payload: ChartGenerationPayload):
        super().__init__(chart_generation_payload=chart_generation_payload)
        self.plots_data: list[PlotGenerationData] = chart_generation_payload.plots

    def get_stacked_bar_chart_config(self) -> dict:
        """
        Builds the configuration for the stacked bar chart.

        Returns:
            The configuration for the stacked bar chart.
        """
        chart_config = self._get_base_chart_config()

        chart_config["barmode"] = "stack"

        return {**chart_config, **self._get_legend_config()}

    def get_butterfly_chart_config(
        self,
        *,
        categories: list[str] | None = None,
        maximum_value: float | None = None,
    ) -> dict:
        """
        Builds the configuration for the butterfly chart.

        Notes:
            Butterfly charts draw horizontal bars, so the axes are
            swapped relative to a standard chart: the y-axis displays
            the primary category labels (eg. age groups) while the
            x-axis displays the mirrored values (eg. case counts).

            The titles are therefore swapped back onto those axes.
            `DualCategoryChartSerializer` accepts the axes from callers
            in the orientation they appear on the chart, then swaps them
            into the internal form where the primary category is always
            carried on `x_axis`. This method reverses that swap for
            display, so a caller's `x_axis_title` ends up labelling the
            horizontal axis, as they would expect.

            The left hand side of the chart is drawn with negated
            values. The x-axis is therefore given explicit ticks which
            are mirrored around zero and labelled with their absolute
            values, so that the recorded values are displayed on both
            sides of the chart.

        Args:
            categories: The ordered primary field values which make up
                the y-axis categories. When provided, these are pinned
                to the axis so that the categories are always drawn in
                the order they were requested, with the first requested
                value at the bottom of the chart.
            maximum_value: The largest recorded value across both sides
                of the chart. When provided, this is used to build the
                mirrored x-axis ticks and to pin the axis range, so that
                both sides of the chart are given equal width.

        Returns:
            The configuration for the butterfly chart.
        """
        tick_font = self._get_tick_font_config()

        yaxis_config = {
            "type": "category",
            "title": {
                "text": self._chart_generation_payload.x_axis_title,
                "font": tick_font,
            },
        }
        if categories:
            yaxis_config["categoryorder"] = "array"
            yaxis_config["categoryarray"] = categories

        xaxis_config = {
            "zeroline": True,
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "title": {
                "text": self._chart_generation_payload.y_axis_title,
                "font": tick_font,
            },
        }
        xaxis_config |= self._get_mirrored_axis_tick_config(maximum_value=maximum_value)

        chart_config = {
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
            "height": self.height,
            "width": self.width,
            "showlegend": True,
            "barmode": "overlay",
            "yaxis": yaxis_config,
            "xaxis": xaxis_config,
        }

        return {**chart_config, **self._get_legend_config()}

    @classmethod
    def _get_mirrored_axis_tick_config(
        cls,
        *,
        maximum_value: float | None,
    ) -> dict:
        """
        Builds the mirrored tick configuration for the butterfly x-axis.

        Args:
            maximum_value: The largest recorded value across both sides
                of the chart.

        Returns:
            The tick values, tick labels and range for the x-axis.
            An empty dict is returned when there is no positive value to
            build the ticks from, which leaves the axis to be
            calculated by the chart library.
        """
        if not maximum_value or maximum_value <= 0:
            return {}

        tick_values, tick_text = cls._build_mirrored_axis_ticks(
            maximum_value=maximum_value
        )
        axis_limit = tick_values[-1]

        return {
            "tickvals": tick_values,
            "ticktext": tick_text,
            "range": [-axis_limit, axis_limit],
        }

    @classmethod
    def _build_mirrored_axis_ticks(
        cls,
        *,
        maximum_value: float,
    ) -> tuple[list[float], list[str]]:
        """
        Builds tick values mirrored around zero, with absolute labels.

        Args:
            maximum_value: The largest recorded value across both sides
                of the chart.

        Returns:
            A tuple of the tick values, which run from the negative to
            the positive end of the axis, and the matching tick labels,
            which are the absolute values of those tick values.
        """
        step = cls._calculate_axis_tick_step(maximum_value=maximum_value)
        steps_either_side = math.ceil(maximum_value / step)

        tick_values = [
            round(index * step, BUTTERFLY_AXIS_TICK_PRECISION)
            for index in range(-steps_either_side, steps_either_side + 1)
        ]
        tick_text = [_format_axis_tick_label(value=abs(x)) for x in tick_values]

        return tick_values, tick_text

    @staticmethod
    def _calculate_axis_tick_step(*, maximum_value: float) -> float:
        """
        Calculates a rounded step to place the axis ticks at.

        Args:
            maximum_value: The largest recorded value across both sides
                of the chart.

        Returns:
            The step between each tick on the axis.
        """
        raw_step = maximum_value / BUTTERFLY_AXIS_TICK_COUNT
        magnitude = 10 ** math.floor(math.log10(raw_step))
        normalized_step = raw_step / magnitude

        multiplier = next(
            axis_tick_multiplier
            for axis_tick_multiplier in BUTTERFLY_AXIS_TICK_STEP_MULTIPLIERS
            if normalized_step <= axis_tick_multiplier
        )

        return multiplier * magnitude

    def _get_legend_config(self) -> dict:
        """
        Builds the configuration for the legend.

        Returns:
            The configuration for the legend.
        """
        legend_config = {
            "font": self._get_tick_font_config(),
            "orientation": "h",
            "y": 1.0,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "bottom",
            "entrywidth": 80,
        }

        if legend_title := self._chart_generation_payload.legend_title:
            legend_config["title"] = {
                "text": f"<b>{legend_title}</b>",
                "side": "top",
            }

        return {
            "legend": legend_config,
        }
