from unittest import mock

import pytest

from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from metrics.domain.models.plots import CompletePlotData, PlotParameters
from metrics.interfaces.downloads.dual_category.access import (
    DualCategoryDownloadsInterface,
    get_dual_category_downloads_data,
)
from metrics.interfaces.plots.dual_category.access import DualCategoryPlotsInterface

MODULE_PATH = "metrics.interfaces.downloads.dual_category.access"


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
        segment_secondary_values=["00-04", "05-11"],
    )


class TestDualCategoryDownloadsInterface:
    @mock.patch(f"{MODULE_PATH}.merge_and_process_timeseries_querysets")
    def test_build_downloads_data_uses_dual_category_plots_interface_for_timeseries(
        self,
        mocked_merge_timeseries: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a dual-category timeseries download request
        When `build_downloads_data()` is called on `DualCategoryDownloadsInterface`
        Then plot data is fetched and merged into a single timeseries queryset
        """
        # Given
        complete_plots = [mock.MagicMock(spec=CompletePlotData)]
        merged_queryset = mock.MagicMock(spec=CoreTimeSeriesQuerySet)
        mocked_merge_timeseries.return_value = merged_queryset

        plots_interface = mock.MagicMock(spec=DualCategoryPlotsInterface)
        plots_interface.build_plots_data_for_full_queryset.return_value = complete_plots

        downloads_interface = DualCategoryDownloadsInterface(
            download_request_params=dual_category_download_request_params,
            dual_category_plots_interface=plots_interface,
        )

        # When
        result = downloads_interface.build_downloads_data()

        # Then
        plots_interface.build_plots_data_for_full_queryset.assert_called_once()
        mocked_merge_timeseries.assert_called_once_with(complete_plots=complete_plots)
        assert result is merged_queryset

    @mock.patch(f"{MODULE_PATH}.merge_and_process_headline_querysets")
    def test_build_downloads_data_uses_dual_category_plots_interface_for_headline(
        self,
        mocked_merge_headline: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a dual-category headline download request
        When `build_downloads_data()` is called on `DualCategoryDownloadsInterface`
        Then plot data is fetched and merged into a single headline queryset
        """
        # Given
        dual_category_download_request_params.metric_group = "headline"
        complete_plots = [mock.MagicMock(spec=CompletePlotData)]
        merged_queryset = mock.MagicMock(spec=CoreHeadlineQuerySet)
        mocked_merge_headline.return_value = merged_queryset

        plots_interface = mock.MagicMock(spec=DualCategoryPlotsInterface)
        plots_interface.build_plots_data_for_full_queryset.return_value = complete_plots

        downloads_interface = DualCategoryDownloadsInterface(
            download_request_params=dual_category_download_request_params,
            dual_category_plots_interface=plots_interface,
        )

        # When
        result = downloads_interface.build_downloads_data()

        # Then
        plots_interface.build_plots_data_for_full_queryset.assert_called_once()
        mocked_merge_headline.assert_called_once_with(complete_plots=complete_plots)
        assert result is merged_queryset

    @mock.patch.object(DualCategoryDownloadsInterface, "build_downloads_data")
    def test_get_dual_category_downloads_data_delegates_to_interface(
        self,
        mocked_build_downloads_data: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a dual-category download request
        When `get_dual_category_downloads_data()` is called
        Then the downloads interface builds and returns the merged queryset
        """
        # Given
        merged_queryset = mock.MagicMock()
        mocked_build_downloads_data.return_value = merged_queryset

        # When
        result = get_dual_category_downloads_data(
            download_request_params=dual_category_download_request_params,
        )

        # Then
        mocked_build_downloads_data.assert_called_once()
        assert result is merged_queryset
