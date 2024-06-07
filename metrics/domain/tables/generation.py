from collections import defaultdict
from typing import Any

from metrics.domain.common.utils import ChartAxisFields
from metrics.domain.models import PlotData


class TabularData:
    def __init__(self, *, plots: list[PlotData]):
        self.plots = plots

        # The list of plot labels
        self.plot_labels: list[str] = []

        # The individual plots combined into one dictionary of dictionaries
        self.combined_plots: dict[str, dict[str, str]] = defaultdict(dict)

        # The headings to use in the table
        self.column_heading: str = "reference"

    def create_tabular_plots(self) -> list[dict[str, str | list[dict]]]:
        """Creates the tabular output for the given plots

        Returns:
            A list of dictionaries showing the plot data in a tabular format

        """
        # Merge all the plots together by x-axis
        self.combine_all_plots()

        # Order plots in chronological order for date-based tables
        self._cast_combined_plots_in_order()

        # Create output in required format
        return self.create_multi_plot_output()

    def add_plot_data_to_combined_plots(
        self, *, plot_data: dict[Any, Any], plot_label: str
    ):
        """Add the values to the combined plots dictionary

        Args:
            plot_data: The raw plot data that is not by date
            plot_label: The label for this plot

        Returns:
            None

        """
        for key, value in plot_data.items():
            self.combined_plots[str(key)].update({plot_label: str(value)})

    def _cast_combined_plots_in_order(self) -> None:
        if self._is_date_based:
            self.combined_plots = dict(
                sorted(self.combined_plots.items(), reverse=True)
            )

    def combine_all_plots(self):
        """Merges the individual plots along the x-axis

        Notes:
            This updates the `combined_plots` instance
            variable with the processed plots data

        Returns:
            None

        """
        for index, plot in enumerate(self.plots, 1):
            plot_label: str = plot.parameters.label or f"Plot{index}"
            self.plot_labels.append(plot_label)

            plot_data: dict = self._build_plot_data(plot=plot)

            self.add_plot_data_to_combined_plots(
                plot_data=plot_data,
                plot_label=plot_label,
            )

    @property
    def _is_date_based(self) -> bool:
        return self.plots[0].parameters.x_axis == ChartAxisFields.date.name

    @staticmethod
    def _build_plot_data(*, plot: PlotData) -> dict:
        return dict(zip(plot.x_axis_values, plot.y_axis_values))

    def create_multi_plot_output(self) -> list[dict[str, str | list[dict]]]:
        """Creates the tabular output for the given plots

        Notes:
            Additional ordering is **not** cast over the combined plots
            before being outputted by this method

        Returns:
            A list of dictionaries showing the plots in tabular format

        """
        tabular_data = []

        for left_column, plot_values in self.combined_plots.items():
            tabular_data.append(
                {
                    self.column_heading: left_column,
                    "values": [
                        {"label": plot_label, "value": plot_values.get(plot_label)}
                        for plot_label in self.plot_labels
                    ],
                }
            )

        return tabular_data
