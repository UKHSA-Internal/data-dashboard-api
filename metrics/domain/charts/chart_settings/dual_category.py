import math

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.single_category import (
    SingleCategoryChartSettings,
)
from metrics.domain.models.plots import ChartGenerationPayload, PlotGenerationData

BUTTERFLY_TARGET_TICKS_PER_SIDE = 4
# Multipliers which produce "rounded" tick steps,
# eg. 1, 2, 2.5 or 5 for any given power of 10
NICE_TICK_STEP_MULTIPLIERS = (1, 2, 2.5, 5, 10)


def _calculate_nice_tick_step(
    *,
    maximum_value: float,
    target_tick_count: int,
) -> float:
    """Calculates a rounded tick step which covers the given `maximum_value`.

    Args:
        maximum_value: The largest absolute value in the plotted data.
        target_tick_count: The number of ticks to aim
            for on each side of the chart.

    Returns:
        A rounded step size, eg. 1, 2, 2.5, 5 or 10
        for the relevant power of 10.

    """
    if maximum_value <= 0:
        return 1

    rough_step = maximum_value / target_tick_count
    magnitude = 10 ** math.floor(math.log10(rough_step))

    for multiplier in NICE_TICK_STEP_MULTIPLIERS:
        step = multiplier * magnitude
        if step >= rough_step:
            return step

    return 10 * magnitude


def _format_tick_label(*, value: float) -> str:
    """Formats the given tick `value` for display on the value axis.

    Args:
        value: The absolute value of the tick.

    Returns:
        The thousands-separated label for the tick,
        with decimal places only included when needed.

    """
    if float(value).is_integer():
        return f"{int(value):,}"

    return f"{value:,.1f}"


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
        plotted_values: list[float] | None = None,
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

        Args:
            categories: The ordered primary field values which make up
                the y-axis categories. When provided, these are pinned
                to the axis so that the categories are always drawn in
                the order they were requested, with the first requested
                value at the bottom of the chart.
            plotted_values: The values which are actually drawn on the
                chart. These are used to scale the value axis, and can
                differ from the raw plot values, since a butterfly chart
                draws a single bar per category, per side.

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
            "xaxis": {
                "zeroline": True,
                "showgrid": True,
                "gridcolor": "rgba(0,0,0,0.05)",
                "title": {
                    "text": self._chart_generation_payload.y_axis_title,
                    "font": tick_font,
                },
                **self._get_butterfly_value_axis_tick_config(
                    plotted_values=plotted_values
                ),
            },
        }

        return {**chart_config, **self._get_legend_config()}

    def _get_butterfly_value_axis_tick_config(
        self,
        *,
        plotted_values: list[float] | None = None,
    ) -> dict:
        """
        Builds the tick values/labels for the butterfly chart's value axis.

        Notes:
            Tick marks are placed at evenly spaced, rounded intervals
            which are mirrored on both sides of zero, and are labelled
            with their absolute (ie. non-negative) value so that both
            sides of the chart remain easy to read.
            The axis range is also kept symmetrical so that the centre
            of the chart stays aligned with zero, giving both sides of
            the chart the same amount of room.

        Args:
            plotted_values: The values which are actually drawn on the
                chart. Falls back to the raw plot values when not given.

        Returns:
            A dict containing the `tickvals`, `ticktext`
            and `range` for the axis.
        """
        if plotted_values is None:
            plotted_values = [
                value for plot in self.plots_data for value in plot.y_axis_values
            ]

        maximum_value = max(
            (abs(float(value)) for value in plotted_values),
            default=0,
        )

        tick_step = _calculate_nice_tick_step(
            maximum_value=maximum_value,
            target_tick_count=BUTTERFLY_TARGET_TICKS_PER_SIDE,
        )
        ticks_per_side = max(math.ceil(maximum_value / tick_step), 1)

        positive_tickvals = [
            tick_step * tick_index for tick_index in range(1, ticks_per_side + 1)
        ]
        tickvals = (
            [-tickval for tickval in reversed(positive_tickvals)]
            + [0]
            + positive_tickvals
        )
        axis_limit = tick_step * ticks_per_side

        return {
            "tickvals": tickvals,
            "ticktext": [_format_tick_label(value=abs(tickval)) for tickval in tickvals],
            "range": [-axis_limit, axis_limit],
        }

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
