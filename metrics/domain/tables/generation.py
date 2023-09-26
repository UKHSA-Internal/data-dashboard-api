from collections import defaultdict
from datetime import date
from typing import Any

from metrics.domain.models import PlotData
from metrics.domain.utils import get_axis_name, get_last_day_of_month


class TabularData:
    def __init__(self, plots: list[PlotData]):
        self.plots = plots

        # The list of plot labels
        self.plot_labels: list[str] = []

        # The individual plots combined into one dictionary of dictionaries
        self.combined_plots: dict[str, dict[str, str]] = defaultdict(dict)

        # The headings to use in the table
        self.column_heading: str = "reference"

    def create_plots_in_tabular_format(self) -> list[dict[str, str]]:
        """Creates the tabular output for the given plots

        Returns:
            A list of dictionaries showing the plot data in a tabular format
        """

        # Merge all the plots together by x axis
        self.combine_list_of_plots()

        # Create output in required format
        tabular_format = self.generate_multi_plot_output()

        return tabular_format

    def create_tabular_plots(self) -> list[dict[str, str]]:
        """Creates the tabular output for the given plots

        Returns:
            A list of dictionaries showing the plot data in a tabular format

        """
        # Merge all the plots together by x axis
        self.combine_all_plots()

        # Create output in required format
        return self.generate_multi_plot_output()

    def collate_data_by_date(self, plot_data: dict[Any, Any], plot_label: str):
        """Add just the last values for each month to the combined plots dictionary

        Args:
            plot_data: The raw plot data that is by date
            plot_label: The label for this plot
        """

        for k, v in plot_data.items():
            month_end = str(get_last_day_of_month(k))
            self.combined_plots[month_end].update({plot_label: str(v)})

    def collate_data_not_by_date(self, plot_data: dict[Any, Any], plot_label: str):
        """Add the values to the combined plots dictionary

        Args:
            plot_data: The raw plot data that is not by date
            plot_label: The label for this plot
        """

        for k, v in plot_data.items():
            self.combined_plots[str(k)].update({plot_label: str(v)})

    def combine_list_of_plots(self):
        """Merges the individual plots along the x axis"""

        for plot_num, plot in enumerate(self.plots, 1):
            plot_label: str = plot.parameters.label or "Plot" + str(plot_num)
            self.plot_labels.append(plot_label)

            self.column_heading = get_axis_name(field_name=plot.parameters.x_axis)

            temp_dict = dict(zip(plot.x_axis_values, plot.y_axis_values))

            if type(plot.x_axis_values[0]) is date:
                self.collate_data_by_date(
                    plot_data=temp_dict,
                    plot_label=plot_label,
                )
            else:
                self.collate_data_not_by_date(
                    plot_data=temp_dict,
                    plot_label=plot_label,
                )

    def combine_all_plots(self):
        """Merges the individual plots along the x axis"""

        for index, plot in enumerate(self.plots, 1):
            plot_label: str = plot.parameters.label or f"Plot{index}"
            self.plot_labels.append(plot_label)

            plot_data = dict(zip(plot.x_axis_values, plot.y_axis_values))

            self.collate_data_not_by_date(
                plot_data=plot_data,
                plot_label=plot_label,
            )

    def generate_multi_plot_output(self):
        """Creates the tabular output for the given plots

        Returns:
            A list of dictionaries showing the plots in tabular format
        """
        tabular_data = []

        for left_column, plot_values in sorted(self.combined_plots.items()):
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
