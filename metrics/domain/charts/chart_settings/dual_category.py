from plotly.graph_objs.indicator.gauge import step

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
                **self.compute_butterfly_charge_xaxis_ticks(values1, values2),
            },
        }

        return {**chart_config, **self._get_legend_config()}

    def compute_butterfly_charge_xaxis_ticks(self, left_data, right_data):


        # 2. Find the largest absolute value in the dataset
        max_val = float(max(max(abs(x) for x in left_data), max(abs(x) for x in right_data)))

        # 3. Base the step size calculation on a maximum allowance of 4 ticks per side
        max_ticks_per_side = 4
        target_step = max_val / max_ticks_per_side

        # 4. Extract the Order of Magnitude (Power of 10)
        if target_step >= 1:
            magnitude = 10 ** (len(str(int(target_step))) - 1)
        else:
            magnitude = 1

        # 5. Normalize and snap to standard Plotly modifiers (1, 2, 5, or 10)
        normalized_step = target_step / magnitude
        if normalized_step <= 1:
            clean_modifier = 1
        elif normalized_step <= 2:
            clean_modifier = 2
        elif normalized_step <= 5:
            clean_modifier = 5
        else:
            clean_modifier = 10

        clean_step = int(clean_modifier * magnitude)

        # ==========================================
        # NEW: Dynamically limit the ticks per side
        # ==========================================
        # Calculate exactly how many steps are actually needed to cover max_val
        actual_ticks_per_side = int((max_val // clean_step) + 1)

        # Cap it at your preferred maximum constraint just in case
        actual_ticks_per_side = min(actual_ticks_per_side, max_ticks_per_side)
        # ==========================================

        # 6. Generate the optimized symmetric arrays
        tick_values = [i * clean_step for i in range(-actual_ticks_per_side, actual_ticks_per_side + 1)]
        tick_labels = [str(abs(val)) for val in tick_values]

        # 7. Establish visual boundary limits tightly matching the active ticks
        axis_limit = actual_ticks_per_side * clean_step

        return {
            "tickmode": "array",
            "tickvals": tick_values,
            "ticktext": tick_labels,
            "range": [-axis_limit - 1, axis_limit + 1],
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
