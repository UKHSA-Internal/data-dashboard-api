
from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.single_category import (
    SingleCategoryChartSettings,
)
from metrics.domain.models.plots import ChartGenerationPayload, PlotGenerationData


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
            },
        }

        return {**chart_config, **self._get_legend_config()}

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
