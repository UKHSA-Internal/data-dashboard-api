from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.domain.common.utils import DataSourceFileType
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from metrics.interfaces.downloads.access import (
    merge_and_process_headline_querysets,
    merge_and_process_timeseries_querysets,
)
from metrics.interfaces.plots.dual_category.access import DualCategoryPlotsInterface


class DualCategoryDownloadsInterface:
    """Builds merged download querysets for dual-category chart data."""

    def __init__(
        self,
        *,
        download_request_params: DualCategoryDownloadRequestParams,
        dual_category_plots_interface: DualCategoryPlotsInterface | None = None,
    ) -> None:
        """Initialise the interface for a dual-category download request.

        Args:
            download_request_params: Validated dual-category download request parameters.
            dual_category_plots_interface: Optional plots interface.
        """
        self.download_request_params = download_request_params
        self.metric_group = download_request_params.metric_group
        self.dual_category_plots_interface = (
            dual_category_plots_interface
            or DualCategoryPlotsInterface(
                chart_request_params=download_request_params,
            )
        )

    def build_downloads_data(
        self,
    ) -> CoreTimeSeriesQuerySet | CoreHeadlineQuerySet:
        """Return a single merged queryset for the dual-category download request.

        Returns:
            Merged queryset for all expanded plots in the request.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots returned data.
        """
        complete_plots = (
            self.dual_category_plots_interface.build_plots_data_for_full_queryset()
        )

        if DataSourceFileType[self.metric_group].is_timeseries:
            return merge_and_process_timeseries_querysets(complete_plots=complete_plots)

        return merge_and_process_headline_querysets(complete_plots=complete_plots)


def get_dual_category_downloads_data(
    *,
    download_request_params: DualCategoryDownloadRequestParams,
) -> CoreTimeSeriesQuerySet | CoreHeadlineQuerySet:
    """Get the final merged queryset for a dual-category downloads export.

    Args:
        download_request_params: Validated dual-category download request parameters.

    Returns:
        Merged queryset containing all records for the requested plots.
    """
    downloads_interface = DualCategoryDownloadsInterface(
        download_request_params=download_request_params,
    )
    return downloads_interface.build_downloads_data()
