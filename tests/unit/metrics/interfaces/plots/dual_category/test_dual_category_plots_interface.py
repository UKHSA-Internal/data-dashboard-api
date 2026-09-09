from unittest import mock

import pytest

from metrics.data.managers.core_models.headline import CoreHeadlineManager
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from metrics.domain.models.plots import CompletePlotData, PlotParameters
from metrics.interfaces.plots.access import PlotsInterface
from metrics.interfaces.plots.dual_category.access import DualCategoryPlotsInterface

MODULE_PATH = "metrics.interfaces.plots.dual_category.access"


@pytest.fixture
def dual_category_download_request_params(
    fake_chart_plot_parameters: PlotParameters,
) -> DualCategoryDownloadRequestParams:
    return DualCategoryDownloadRequestParams(
        metric_group="cases",
        plots=[fake_chart_plot_parameters],
        file_format="json",
        chart_height=260,
        chart_width=700,
        x_axis="date",
        y_axis="metric",
        secondary_category="age",
        segment_secondary_values=["00-04"],
    )


class TestDualCategoryPlotsInterface:
    @mock.patch(f"{MODULE_PATH}.PlotsInterface")
    def test_build_plots_data_for_full_queryset_delegates_to_plots_interface(
        self,
        mocked_plots_interface_class: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a `DualCategoryPlotsInterface` with an injected `PlotsInterface`
        When `build_plots_data_for_full_queryset()` is called
        Then plot data is fetched via the underlying `PlotsInterface`
        """
        # Given
        complete_plots = [mock.MagicMock(spec=CompletePlotData)]
        mocked_plots_interface = mock.MagicMock(spec=PlotsInterface)
        mocked_plots_interface.build_plots_data_for_full_queryset.return_value = (
            complete_plots
        )
        mocked_plots_interface_class.return_value = mocked_plots_interface

        interface = DualCategoryPlotsInterface(
            chart_request_params=dual_category_download_request_params,
            plots_interface=mocked_plots_interface,
        )

        # When
        result = interface.build_plots_data_for_full_queryset()

        # Then
        mocked_plots_interface.build_plots_data_for_full_queryset.assert_called_once()
        assert result == complete_plots

    def test_uses_headline_manager_for_headline_metric_group(
        self,
        fake_chart_plot_parameters_headline_data: PlotParameters,
    ):
        """
        Given a dual-category download request for a headline metric group
        When `DualCategoryPlotsInterface` is initialised
        Then the core model manager is a `CoreHeadlineManager`
        """
        # Given
        request_params = DualCategoryDownloadRequestParams(
            metric_group="headline",
            plots=[fake_chart_plot_parameters_headline_data],
            file_format="json",
            chart_height=260,
            chart_width=700,
            x_axis="age",
            y_axis="metric",
            secondary_category="sex",
            segment_secondary_values=["f"],
        )

        # When
        interface = DualCategoryPlotsInterface(chart_request_params=request_params)

        # Then
        assert isinstance(interface.core_model_manager, CoreHeadlineManager)
