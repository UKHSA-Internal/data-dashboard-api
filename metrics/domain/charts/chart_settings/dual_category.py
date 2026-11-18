from itertools import chain

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.single_category import (
    SingleCategoryChartSettings,
)
from metrics.domain.models.plots import ChartGenerationPayload, PlotGenerationData

PLOTLY_STEPS = [1, 2, 5, 10, 15]
MAX_TICKS_PER_SIDE = 5
PADDING_PERCENTAGE = 0.05

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

    def get_butterfly_chart_config(self, values1: list[float], values2: list[float]) -> dict:

        tick_font = self._get_tick_font_config()
        # yaxis_config = {
        #     "type": "category",
        #     "fixedrange": True,
        #     "title": {
        #         "text": self._chart_generation_payload.y_axis_title,
        #         "font": tick_font,
        #     },
        #     "ticklabeloverflow": "allow",
        #     "automargin": True,
        # }

        # chart_config = {
        #     "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
        #     "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
        #     "hoverlabel": {
        #         "align": "left",
        #         "bgcolor": "white",
        #     },
        #     "margin": {
        #         "l": 0,
        #         "r": 0,
        #         "b": 0,
        #         "t": 0,
        #     },
        #     "autosize": False,
        #     "height": self.height,
        #     "width": self.width,
        #     "showlegend": True,
        #     "barmode": "overlay",
        #     "yaxis": yaxis_config,
        #     "xaxis": {
        #         "ticklabeloverflow": "allow",
        #         "automargin": True,
        #         "zeroline": True,
        #         "showgrid": True,
        #         "gridcolor": "rgba(0,0,0,0.05)",
        #         "fixedrange": True,
        #         "title": {
        #             "text": self._chart_generation_payload.x_axis_title,
        #             "font": tick_font,
        #         },
        #         **self.compute_butterfly_charge_xaxis_ticks(values1, values2),
        #     },
        # }

        chart_config = self._get_base_chart_config()

        chart_config["barmode"] = "overlay"

        yaxis = chart_config["yaxis"]
        updated_yaxis = {**yaxis, "type":"category"}
        chart_config["yaxis"] = updated_yaxis

        xaxis = chart_config["xaxis"]
        updated_xaxis = {**xaxis, **self.compute_butterfly_charge_xaxis_ticks(values1, values2)}
        chart_config["xaxis"] = updated_xaxis

        return {**chart_config, **self._get_legend_config()}

    @staticmethod
    def compute_butterfly_charge_xaxis_ticks(left_data: list[float], right_data: list[float]) -> dict:

        # Find the largest absolute value in the dataset
        max_val = float(max(abs(x) for x in chain(left_data, right_data)))

        # Base the step size calculation on a maximum allowance of 4 ticks per side
        target_step = max_val / MAX_TICKS_PER_SIDE

        # Extract the Order of Magnitude (Power of 10)
        magnitude = 10 ** max(0, len(str(int(target_step))) - 1)

        # Normalize and snap to standard Plotly modifiers (1, 2, 5, or 10)
        clean_step = int(
            next(
                (m for m in PLOTLY_STEPS if target_step / magnitude <= m),
                PLOTLY_STEPS[-1],
            )
            * magnitude
        )

        # Calculate exactly how many steps are actually needed to cover max_val
        actual_ticks_per_side = int((max_val // clean_step) + 1)

        # Cap it at your preferred maximum constraint just in case
        actual_ticks_per_side = min(actual_ticks_per_side, MAX_TICKS_PER_SIDE)
        # ==========================================

        # Generate the optimized symmetric arrays
        tick_values = [
            i * clean_step
            for i in range(-actual_ticks_per_side, actual_ticks_per_side + 1)
        ]
        tick_labels = [str(abs(val)) for val in tick_values]

        # Establish visual boundary limits tightly matching the active ticks
        axis_limit = actual_ticks_per_side * clean_step

        # Calculate padding relative to the axis limit and use that to pad the axis negatively and positively.
        padding = axis_limit * PADDING_PERCENTAGE

        return {
            "tickmode": "array",
            "tickvals": tick_values,
            "ticktext": tick_labels,
            "range": [-axis_limit - padding, axis_limit + padding],
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
