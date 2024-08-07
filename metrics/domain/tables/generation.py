import datetime
from collections import defaultdict
from decimal import Decimal

from metrics.domain.common.utils import ChartAxisFields
from metrics.domain.models import PlotData

IN_REPORTING_DELAY_PERIOD = "in_reporting_delay_period"

PLOT_DATA_LOOKUP_TYPE = dict[datetime.date, Decimal]
IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE = dict[datetime.date, bool]


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
        self,
        *,
        plot_data: PLOT_DATA_LOOKUP_TYPE,
        plot_label: str,
        in_reporting_delay_period_lookup: (
            IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE | None
        ) = None,
    ):
        """Add the values to the combined plots dictionary

        Args:
            plot_data: The raw plot data that is not by date
            plot_label: The label for this plot
            in_reporting_delay_period_lookup: The lookups for
                the reporting delay period associated with
                each data point in the `plot_data`

        Returns:
            None

        """
        in_reporting_delay_period_lookup = in_reporting_delay_period_lookup or {}

        for key, value in plot_data.items():
            result = {plot_label: str(value)}
            in_reporting_delay_period_value = self._fetch_reporting_delay_period(
                in_reporting_delay_period_lookup=in_reporting_delay_period_lookup,
                key=key,
            )
            result[IN_REPORTING_DELAY_PERIOD] = in_reporting_delay_period_value

            self.combined_plots[str(key)].update(result)

    @classmethod
    def _fetch_reporting_delay_period(
        cls,
        in_reporting_delay_period_lookup: IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE,
        key: datetime.date,
    ) -> bool:
        try:
            return in_reporting_delay_period_lookup[key]
        except KeyError:
            return False

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

            plot_data: PLOT_DATA_LOOKUP_TYPE = self._build_plot_data_for_axes_values(
                plot=plot
            )
            in_reporting_delay_period_lookup: IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE = (
                self._build_plot_data_for_in_reporting_delay_period_values(plot=plot)
            )

            self.add_plot_data_to_combined_plots(
                plot_data=plot_data,
                plot_label=plot_label,
                in_reporting_delay_period_lookup=in_reporting_delay_period_lookup,
            )

    @property
    def _is_date_based(self) -> bool:
        return self.plots[0].parameters.x_axis == ChartAxisFields.date.name

    @classmethod
    def _build_plot_data_for_axes_values(
        cls, *, plot: PlotData
    ) -> PLOT_DATA_LOOKUP_TYPE:
        return dict(zip(plot.x_axis_values, plot.y_axis_values))

    @classmethod
    def _build_plot_data_for_in_reporting_delay_period_values(
        cls, *, plot: PlotData
    ) -> IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE:
        try:
            in_report_delay_period_values = plot.additional_values[
                IN_REPORTING_DELAY_PERIOD
            ]
        except (KeyError, TypeError):
            in_report_delay_period_values = [
                False for _ in range(len(plot.x_axis_values))
            ]

        return dict(zip(plot.x_axis_values, in_report_delay_period_values))

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
                        {
                            "label": plot_label,
                            "value": plot_values.get(plot_label),
                            IN_REPORTING_DELAY_PERIOD: plot_values.get(
                                IN_REPORTING_DELAY_PERIOD, False
                            ),
                        }
                        for plot_label in self.plot_labels
                    ],
                }
            )

        return tabular_data
