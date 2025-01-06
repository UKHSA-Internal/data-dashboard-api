import datetime
from collections import defaultdict
from decimal import Decimal

from metrics.domain.common.utils import (
    ChartAxisFields,
    DataSourceFileType,
    extract_metric_group_from_metric,
)

IN_REPORTING_DELAY_PERIOD = "in_reporting_delay_period"

PLOT_DATA_LOOKUP_TYPE = dict[datetime.date, Decimal]
IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE = dict[datetime.date, bool]

DEFAULT_PLOT_LABEL = "Plot"


class TabularData:
    def __init__(self, *, plots: list["PlotGenerationData"]):
        self.plots = plots
        self.metric_group = extract_metric_group_from_metric(
            metric=self.plots[0].parameters.metric
        )

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
            plot_label: str = plot.parameters.label or f"{DEFAULT_PLOT_LABEL}{index}"
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
        cls, *, plot: "PlotGenerationData"
    ) -> PLOT_DATA_LOOKUP_TYPE:
        return dict(zip(plot.x_axis_values, plot.y_axis_values))

    @classmethod
    def _build_plot_data_for_in_reporting_delay_period_values(
        cls, *, plot: "PlotGenerationData"
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

    def create_multi_plot_output(self) -> list[dict[str, str] | list[dict]]:
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
                self.create_multi_plot_row(
                    left_column=left_column,
                    plot_values=plot_values,
                )
            )

        return tabular_data

    def create_multi_plot_row(
        self, left_column: str, plot_values: dict[str, str]
    ) -> dict[str, str | list[dict]]:
        """Creates a row for tabular data output

        Notes:
            When creating a chart based on `CoreHeadline` data
            if a `plot_label` is provided it should replace `left_column`
            so that the label is returned in the `reference` field.

        Returns:
            A dictionary representing the tabular row returned
            Eg. {"reference": "Age", "values": [{"label": "Amount", "value": 53.00, IN_REPORTING_DELAY_PERIOD: False}]}
        """
        row = {self.column_heading: left_column, "values": []}

        if DataSourceFileType[self.metric_group].is_timeseries:
            row["values"].extend(
                self.create_timeseries_plot_values(plot_values=plot_values)
            )

        if DataSourceFileType[self.metric_group].is_headline:
            current_plot_label = next(iter(plot_values))

            if DEFAULT_PLOT_LABEL not in current_plot_label:
                row[self.column_heading] = current_plot_label

            row["values"].extend(
                self.create_headline_plot_values(plot_values=plot_values)
            )

        return row

    def create_timeseries_plot_values(self, plot_values: dict[str, str]) -> list[dict]:
        """Creates an array of values for times series tabular data row

        Returns:
            A list of dictionaries representing a plot and its values
            Eg. [{label: "Plot1", value: "55", IN_REPORTING_DELAY_PERIOD: False}]
        """
        return [
            {
                "label": plot_label,
                "value": plot_values.get(plot_label),
                IN_REPORTING_DELAY_PERIOD: plot_values.get(
                    IN_REPORTING_DELAY_PERIOD, False
                ),
            }
            for plot_label in self.plot_labels
        ]

    def create_headline_plot_values(self, plot_values: dict[str, str]) -> list[dict]:
        """Creates an array of values for times series tabular data row

        Notes:
            For headline tabular data the label for each plot
            is set to `Amount` to keep all values in the same

        Returns:
            A list of dictionaries representing a plot and its values
            Eg. [{label: "Amount", value: "55", IN_REPORTING_DELAY_PERIOD: False}]
        """
        return [
            {
                "label": "Amount",
                "value": plot_values.get(plot_label),
                IN_REPORTING_DELAY_PERIOD: False,
            }
            for plot_label in self.plot_labels
            if plot_values.get(plot_label)
        ]
