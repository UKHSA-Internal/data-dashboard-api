from metrics.domain.models import ChartRequestParams
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)
from metrics.interfaces.tables.access import generate_table_for_full_plots


def generate_subplot_table(
    *, request_params_per_group: list[ChartRequestParams]
) -> list[dict]:
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
