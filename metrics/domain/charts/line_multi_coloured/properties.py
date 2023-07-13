from enum import Enum

from metrics.domain.models import PlotData


class ChartLineTypes(Enum):
    SOLID = "solid"
    DASH = "dash"

    @classmethod
    def choices(cls):
        return tuple((chart_type.name, chart_type.name) for chart_type in cls)

    @classmethod
    def get_chart_line_type(cls, line_type: str) -> "ChartLineTypes":
        try:
            return cls[line_type]
        except KeyError:
            return cls.SOLID


def is_legend_required(chart_plots_data: list[PlotData]) -> bool:
    """Checks if any of the `PlotData` models contains a truthy `label` attribute.

    chart_plots_data: List of `PlotData` models,
            where each model represents a requested plot.

    Returns:
        True if at least one of the `PlotData` models
        contains a truthy `label` attribute.
        False otherwise.

    """
    return any(plot_data.parameters.label for plot_data in chart_plots_data)
