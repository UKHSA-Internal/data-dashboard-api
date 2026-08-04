from django.db.models import Manager

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.common.utils import (
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from metrics.domain.models.plots import CompletePlotData
from metrics.interfaces.plots.access import PlotsInterface
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class DualCategoryPlotsInterface:
    """Fetches full querysets for dual-category download plots via PlotsInterface."""

    def __init__(
        self,
        *,
        chart_request_params: DualCategoryDownloadRequestParams,
        core_model_manager: CORE_MODEL_MANAGER_TYPE | None = None,
        plots_interface: PlotsInterface | None = None,
    ) -> None:
        """Initialise the interface for a dual-category download request.

        Args:
            chart_request_params: Expanded dual-category download request parameters.
            core_model_manager: Optional Django manager override for the metric group.
            plots_interface: Optional `PlotsInterface` override for testing.
        """
        self.chart_request_params = chart_request_params
        self.metric_group = extract_metric_group_from_metric(
            metric=self.chart_request_params.plots[0].metric
        )
        self.core_model_manager = core_model_manager or self._get_core_model_manager()
        self.plots_interface = plots_interface or PlotsInterface(
            chart_request_params=self.chart_request_params,
            core_model_manager=self.core_model_manager,
        )

    def _get_core_model_manager(self) -> Manager:
        """Return the core model manager for the request metric group.

        Returns:
            `CoreTimeSeries` manager for timeseries metrics, otherwise `CoreHeadline`.
        """
        if DataSourceFileType[self.metric_group].is_timeseries:
            return DEFAULT_CORE_TIME_SERIES_MANAGER

        return DEFAULT_CORE_HEADLINE_MANAGER

    def build_plots_data_for_full_queryset(self) -> list[CompletePlotData]:
        """Return complete plot data with full querysets for each expanded plot.

        Returns:
            List of `CompletePlotData` models for each requested plot.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots returned data.
        """
        return self.plots_interface.build_plots_data_for_full_queryset()
