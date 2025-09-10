from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.domain.models import ChartRequestParams
from metrics.interfaces.downloads.access import get_downloads_data
from metrics.interfaces.plots.access import DataNotFoundForAnyPlotError


class SubplotDownloadsInterface:
    def __init__(
        self, *, charts_request_param_models: list[ChartRequestParams]
    ) -> None:
        self._charts_request_param_models = charts_request_param_models
        self._metric_group = charts_request_param_models[0].metric_group

    def _get_starting_point_queryset(
        self,
    ) -> CoreHeadlineQuerySet | CoreTimeSeriesQuerySet:
        queryset_class = (
            CoreHeadlineQuerySet
            if self._metric_group == "headline"
            else CoreTimeSeriesQuerySet
        )
        return queryset_class().none()

    def get_combined_subplot_data(self):
        combined_queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet = (
            self._get_starting_point_queryset()
        )

        for charts_request_param in self._charts_request_param_models:
            try:
                queryset: CoreTimeSeriesQuerySet = get_downloads_data(
                    chart_plots=charts_request_param
                )
            except DataNotFoundForAnyPlotError:
                continue

            combined_queryset |= queryset

        return combined_queryset


def get_subplot_downloads_data(
    *, charts_request_param_models: list[ChartRequestParams]
) -> CoreTimeSeriesQuerySet:
    """Gets the final queryset for the subplot downloads for with the given `charts_request_param_models`

    Args:
        charts_request_param_models: The data models representing
            the requested sub plot groups for the downloads export

    Returns:
        A single queryset containing the merged results
        in chronological order, starting from the latest records.
        Grouped as dictated by the subplot groups

    """
    subplot_downloads_interface = SubplotDownloadsInterface(
        charts_request_param_models=charts_request_param_models
    )
    return subplot_downloads_interface.get_combined_subplot_data()
