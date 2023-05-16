from typing import Dict, List

from metrics.domain.models import ChartPlotData, ChartPlots
from metrics.domain.tabular.generation import create_plots_in_tabular_format
from metrics.interfaces.charts.access import (
    ChartsInterface,
    validate_each_requested_chart_plot,
)


class TabularInterface(ChartsInterface):
    # Inherit from ChartsInterface to avoid replication

    def generate_plots_for_table(self) -> List[Dict[str, str]]:
        """Create a list of plots from the request

        Returns:
            The requested plots in tabular format
        """
        plots_data: List[ChartPlotData] = self.build_chart_plots_data()

        return create_plots_in_tabular_format(
            chart_plots_data=plots_data,
        )


def generate_tabular_output(chart_plots: ChartPlots) -> str:
    """Validates and creates tabular output based off the parameters provided within the `chart_plots` model

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format
    """
    validate_each_requested_chart_plot(chart_plots=chart_plots)

    library = TabularInterface(chart_plots=chart_plots)
    tabular_output = library.generate_plots_for_table()

    return tabular_output
