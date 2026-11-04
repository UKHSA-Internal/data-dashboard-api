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

    def get_butterfly_chart_config(self, values1, values2) -> dict:
        left_wing_data = values1  # Plotted negatively
        right_wing_data = values2

        # 2. Find the single largest absolute value to ensure perfect symmetry around 0
        max_val = float(max(max(abs(x) for x in left_wing_data), max(abs(x) for x in right_wing_data)))

        # 3. Determine a clean, rounded step size (e.g., ticking by 10s, 20s, or 50s)
        # Let's say we want 4 ticks on each side of zero (9 total ticks including 0)
        ticks_per_side = 4
        step = int(round(max_val / ticks_per_side))

        # 4. Generate the symmetric tick positions from negative max to positive max
        # Using an odd number of total ticks ensures 0 sits dead-centre
        tick_values = [i * step for i in range(-ticks_per_side, ticks_per_side + 1)]

        # 5. Map the tick positions to absolute (positive) strings
        tick_labels = [str(abs(val)) for val in tick_values]

        tick_font = self._get_tick_font_config()
        yaxis_config = {
            "type": "category",
            "title": {
                "text": self._chart_generation_payload.y_axis_title,
                "font": tick_font,
            },
        }

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
            # "autosize": False,
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
                    "text": self._chart_generation_payload.x_axis_title,
                    "font": tick_font,
                },
                "tickmode":"array",
                "tickvals":tick_values,
                "ticktext":tick_labels,
                "range": [-max_val - (step * 0.5), max_val + (step * 0.5)]
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
