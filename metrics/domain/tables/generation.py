import datetime
from collections import defaultdict
from decimal import Decimal

from metrics.domain.common.utils import (
    ChartAxisFields,
    DataSourceFileType,
    extract_metric_group_from_metric,
)

IN_REPORTING_DELAY_PERIOD = "in_reporting_delay_period"
UPPER_CONFIDENCE = "upper_confidence"
LOWER_CONFIDENCE = "lower_confidence"

PLOT_DATA_LOOKUP_TYPE = dict[datetime.date, Decimal]
IN_REPORTING_DELAY_PERIOD_LOOKUP_TYPE = dict[datetime.date, bool]
CONFIDENCE_LOOKUP_TYPE = dict[datetime.date, Decimal | None]

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
        upper_confidence_lookup: CONFIDENCE_LOOKUP_TYPE | None = None,
        lower_confidence_lookup: CONFIDENCE_LOOKUP_TYPE | None = None,
    ):
        """Add the values to the combined plots dictionary

        Args:
            plot_data: The raw plot data that is not by date
            plot_label: The label for this plot
            in_reporting_delay_period_lookup: The lookups for
                the reporting delay period associated with
                each data point in the `plot_data`
            upper_confidence_lookup: The lookups for upper confidence
                intervals associated with each data point
            lower_confidence_lookup: The lookups for lower confidence
                intervals associated with each data point

        Returns:
            None

        """
        in_reporting_delay_period_lookup = in_reporting_delay_period_lookup or {}
        upper_confidence_lookup = upper_confidence_lookup or {}
        lower_confidence_lookup = lower_confidence_lookup or {}

        for key, value in plot_data.items():
            result = {plot_label: str(value)}
            in_reporting_delay_period_value = self._fetch_reporting_delay_period(
                in_reporting_delay_period_lookup=in_reporting_delay_period_lookup,
                key=key,
            )
            result[IN_REPORTING_DELAY_PERIOD] = in_reporting_delay_period_value

            upper_confidence_value = self._fetch_confidence_value(
                confidence_lookup=upper_confidence_lookup,
                key=key,
            )
            if upper_confidence_value is not None:
                result[UPPER_CONFIDENCE] = str(upper_confidence_value)

            lower_confidence_value = self._fetch_confidence_value(
                confidence_lookup=lower_confidence_lookup,
                key=key,
            )
            if lower_confidence_value is not None:
                result[LOWER_CONFIDENCE] = str(lower_confidence_value)

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

    @classmethod
    def _fetch_confidence_value(
        cls,
        confidence_lookup: CONFIDENCE_LOOKUP_TYPE,
        key: datetime.date,
    ) -> Decimal | None:
        try:
            return confidence_lookup[key]
        except KeyError:
            return None

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
            upper_confidence_lookup: CONFIDENCE_LOOKUP_TYPE = (
                self._build_plot_data_for_confidence_values(
                    plot=plot, confidence_field=UPPER_CONFIDENCE
                )
            )
            lower_confidence_lookup: CONFIDENCE_LOOKUP_TYPE = (
                self._build_plot_data_for_confidence_values(
                    plot=plot, confidence_field=LOWER_CONFIDENCE
                )
            )

            self.add_plot_data_to_combined_plots(
                plot_data=plot_data,
                plot_label=plot_label,
                in_reporting_delay_period_lookup=in_reporting_delay_period_lookup,
                upper_confidence_lookup=upper_confidence_lookup,
                lower_confidence_lookup=lower_confidence_lookup,
            )

    @property
    def _is_date_based(self) -> bool:
        return self.plots[0].parameters.x_axis == ChartAxisFields.date.name

    @classmethod
    def _build_plot_data_for_axes_values(
        cls, *, plot: "PlotGenerationData"
    ) -> PLOT_DATA_LOOKUP_TYPE:
        return dict(zip(plot.x_axis_values, plot.y_axis_values, strict=False))

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

        return dict(
            zip(plot.x_axis_values, in_report_delay_period_values, strict=False)
        )

    @classmethod
    def _build_plot_data_for_confidence_values(
        cls, *, plot: "PlotGenerationData", confidence_field: str
    ) -> CONFIDENCE_LOOKUP_TYPE:
        """Builds a lookup dictionary for confidence interval values

        Args:
            plot: The plot data containing confidence intervals
            confidence_field: The field name for the confidence interval
                (either "upper_confidence" or "lower_confidence")

        Returns:
            A dictionary mapping x-axis values to confidence interval values
        """
        try:
            confidence_values = plot.additional_values[confidence_field]
        except (KeyError, TypeError):
            confidence_values = [None for _ in range(len(plot.x_axis_values))]

        return dict(zip(plot.x_axis_values, confidence_values, strict=False))

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
            Eg. [{label: "Plot1", value: "55", IN_REPORTING_DELAY_PERIOD: False, upper_confidence: "60", lower_confidence: "50"}]
        """
        result = []
        for plot_label in self.plot_labels:
            value_dict = {
                "label": plot_label,
                "value": plot_values.get(plot_label),
                IN_REPORTING_DELAY_PERIOD: plot_values.get(
                    IN_REPORTING_DELAY_PERIOD, False
                ),
            }
            if UPPER_CONFIDENCE in plot_values:
                value_dict[UPPER_CONFIDENCE] = plot_values.get(UPPER_CONFIDENCE)
            if LOWER_CONFIDENCE in plot_values:
                value_dict[LOWER_CONFIDENCE] = plot_values.get(LOWER_CONFIDENCE)
            result.append(value_dict)
        return result

    def create_headline_plot_values(self, plot_values: dict[str, str]) -> list[dict]:
        """Creates an array of values for times series tabular data row

        Notes:
            For headline tabular data the label for each plot
            is set to `Amount` to keep all values in the same

        Returns:
            A list of dictionaries representing a plot and its values
            Eg. [{label: "Amount", value: "55", IN_REPORTING_DELAY_PERIOD: False, upper_confidence: "60", lower_confidence: "50"}]
        """
        result = []
        for plot_label in self.plot_labels:
            if plot_values.get(plot_label):
                value_dict = {
                    "label": "Amount",
                    "value": plot_values.get(plot_label),
                    IN_REPORTING_DELAY_PERIOD: False,
                }
                if UPPER_CONFIDENCE in plot_values:
                    value_dict[UPPER_CONFIDENCE] = plot_values.get(UPPER_CONFIDENCE)
                if LOWER_CONFIDENCE in plot_values:
                    value_dict[LOWER_CONFIDENCE] = plot_values.get(LOWER_CONFIDENCE)
                result.append(value_dict)
        return result
