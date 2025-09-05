from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)
from metrics.interfaces.tables.access import generate_table_for_full_plots


def generate_subplot_table(
    *, subplot_chart_parameters: SubplotChartRequestParameters
) -> list[dict]:
    request_params_per_group: list[ChartRequestParams] = (
        subplot_chart_parameters.output_payload_for_tables()
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
