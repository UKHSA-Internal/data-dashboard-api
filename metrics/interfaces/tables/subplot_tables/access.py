from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.domain.tables.generation import IN_REPORTING_DELAY_PERIOD
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)
from metrics.interfaces.tables.access import generate_table_for_full_plots


class SubplotTablesInterface:
    def __init__(
        self,
        *,
        request_params: SubplotChartRequestParameters,
    ):
        self.request_params = request_params

    def generate_full_plots_for_table(self) -> list[dict]:
        request_params_per_group: list[ChartRequestParams] = (
            self.request_params.output_payload_for_tables()
        )

        result: list[dict] = []

        for request_params in request_params_per_group:
            try:
                tabular_data_for_sub_plot: list[dict[str, str]] = (
                    generate_table_for_full_plots(request_params=request_params)
                )
            except (InvalidPlotParametersError, DataNotFoundForAnyPlotError):
                tabular_data_for_sub_plot = (
                    self._get_placeholder_for_sub_plot_with_no_tabular_data(
                        request_params=request_params
                    )
                )

            tabular_data_for_sub_plot = self._inject_null_values_for_any_missing_plots(
                tabular_data_for_sub_plot=tabular_data_for_sub_plot,
                request_params=request_params,
            )

            result += tabular_data_for_sub_plot

        if not result:
            raise DataNotFoundForAnyPlotError

        return result

    @classmethod
    def _inject_null_values_for_any_missing_plots(
        cls,
        *,
        tabular_data_for_sub_plot: list[dict],
        request_params: ChartRequestParams,
    ) -> list[dict]:
        """Ensure each row contains null value placeholders for any missing plots

        Args:
            tabular_data_for_sub_plot: A list of tabular row dicts (one per group),
                each with keys 'reference' and 'values'.
            request_params: The `ChartRequestParams` model for this group,
                whose plots define the required order and labels.

        Returns:
            The same list of rows with 'values' arrays ordered to match plots on the `ChartRequestParams`
            and with missing entries covered as null case placeholders

        """
        required_labels: list[str] = [plot.label for plot in request_params.plots]

        current_values = tabular_data_for_sub_plot[0]["values"]
        label_lookup = {item.get("label"): item for item in current_values}

        complete_values: list[dict] = []
        for label in required_labels:
            try:
                value = label_lookup[label]
            except KeyError:
                value = {
                    "label": label,
                    "value": None,
                    IN_REPORTING_DELAY_PERIOD: False,
                }
            complete_values.append(value)

        tabular_data_for_sub_plot[0]["values"] = complete_values

        return tabular_data_for_sub_plot

    @classmethod
    def _get_placeholder_for_sub_plot_with_no_tabular_data(
        cls, *, request_params: ChartRequestParams
    ) -> list[dict]:
        """Create a placeholder row for a subplot group that returned no data at all.

        Returns a list with a single row containing the 'reference' for this group and
        'values' filled with None placeholders for each expected plot label in order.
        """
        x_axis_selector = request_params.x_axis
        reference = getattr(request_params.plots[0], x_axis_selector)
        return [{"reference": reference, "values": []}]


def generate_subplot_table(
    *, subplot_chart_parameters: SubplotChartRequestParameters
) -> list[dict]:
    """Validates and creates tabular output for the given `subplot_chart_parameters

    Args:
        subplot_chart_parameters: The requested subplot table
            parameters encapsulated as a model

    Returns:
        The requested data in tabular format

    Raises:
        `DataNotFoundForAnyPlotError`: If no subplots
            returned any data from the underlying queries
    """

    subplot_tables_interface = SubplotTablesInterface(
        request_params=subplot_chart_parameters,
    )
    return subplot_tables_interface.generate_full_plots_for_table()
