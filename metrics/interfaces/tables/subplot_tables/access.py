from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
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
                continue
            result += tabular_data_for_sub_plot

        if not result:
            raise DataNotFoundForAnyPlotError

        return result


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
