import inspect
from http import HTTPStatus
from unittest import mock

import pytest
from rest_framework.response import Response

from metrics.api.views.downloads.dual_category_downloads import (
    DualCategoryDownloadsView,
    EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD,
)
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from metrics.domain.models.plots import PlotParameters
from metrics.interfaces.plots.access import DataNotFoundForAnyPlotError

MODULE_PATH = "metrics.api.views.downloads.dual_category_downloads"
UNWRAPPED_POST = inspect.unwrap(DualCategoryDownloadsView.post)


def _build_request(*, payload: dict) -> mock.MagicMock:
    request = mock.MagicMock()
    request.data = payload
    return request


@pytest.fixture
def dual_category_download_request_params(
    fake_chart_plot_parameters_headline_data: PlotParameters,
) -> DualCategoryDownloadRequestParams:
    return DualCategoryDownloadRequestParams(
        metric_group="headline",
        plots=[fake_chart_plot_parameters_headline_data],
        file_format="json",
        chart_height=260,
        chart_width=700,
        x_axis="age",
        y_axis="metric",
        secondary_category="sex",
        segment_secondary_values=["f", "m"],
        primary_field_values=["00-01"],
    )


class TestDualCategoryDownloadsView:
    @mock.patch(f"{MODULE_PATH}.DualCategoryDownloadSerializer")
    @mock.patch(f"{MODULE_PATH}.get_dual_category_downloads_data")
    def test_post_returns_json_download(
        self,
        mocked_get_downloads_data: mock.MagicMock,
        mocked_serializer_class: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a valid dual-category download request with `file_format` set to `json`
        When `post()` is called on `DualCategoryDownloadsView`
        Then the JSON download handler is invoked and its response is returned
        """
        # Given
        mocked_queryset = mock.MagicMock()
        mocked_get_downloads_data.return_value = mocked_queryset
        mocked_serializer = mock.MagicMock()
        mocked_serializer.data = {"file_format": "json"}
        mocked_serializer.to_models.return_value = dual_category_download_request_params
        mocked_serializer_class.return_value = mocked_serializer

        view = DualCategoryDownloadsView()
        json_response = Response([{"age": "00-01", "f": 1.0, "m": 2.0}])
        view._handle_json = mock.MagicMock(return_value=json_response)

        request = _build_request(payload=EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD)

        # When
        response = UNWRAPPED_POST(view, request)

        # Then
        mocked_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mocked_get_downloads_data.assert_called_once_with(
            download_request_params=dual_category_download_request_params,
        )
        view._handle_json.assert_called_once_with(
            queryset=mocked_queryset,
            chart_plot_models=dual_category_download_request_params,
        )
        assert response is json_response

    @mock.patch(f"{MODULE_PATH}.DualCategoryDownloadSerializer")
    @mock.patch(f"{MODULE_PATH}.get_dual_category_downloads_data")
    def test_post_returns_csv_download(
        self,
        mocked_get_downloads_data: mock.MagicMock,
        mocked_serializer_class: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a valid dual-category download request with `file_format` set to `csv`
        When `post()` is called on `DualCategoryDownloadsView`
        Then the CSV download handler is invoked and its response is returned
        """
        # Given
        mocked_queryset = mock.MagicMock()
        mocked_get_downloads_data.return_value = mocked_queryset
        mocked_serializer = mock.MagicMock()
        mocked_serializer.data = {"file_format": "csv"}
        mocked_serializer.to_models.return_value = dual_category_download_request_params
        mocked_serializer_class.return_value = mocked_serializer

        view = DualCategoryDownloadsView()
        csv_response = mock.MagicMock()
        view._handle_csv = mock.MagicMock(return_value=csv_response)

        request = _build_request(
            payload={
                **EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD,
                "file_format": "csv",
            },
        )

        # When
        response = UNWRAPPED_POST(view, request)

        # Then
        view._handle_csv.assert_called_once_with(
            queryset=mocked_queryset,
            chart_plot_models=dual_category_download_request_params,
        )
        assert response is csv_response

    @mock.patch(f"{MODULE_PATH}.DualCategoryDownloadSerializer")
    @mock.patch(f"{MODULE_PATH}.get_dual_category_downloads_data")
    def test_post_returns_bad_request_when_no_data_found(
        self,
        mocked_get_downloads_data: mock.MagicMock,
        mocked_serializer_class: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given a dual-category download request where no plot data is found
        When `post()` is called on `DualCategoryDownloadsView`
        Then a `400 Bad Request` response is returned with an error message
        """
        # Given
        mocked_get_downloads_data.side_effect = DataNotFoundForAnyPlotError()
        mocked_serializer = mock.MagicMock()
        mocked_serializer.data = {"file_format": "json"}
        mocked_serializer.to_models.return_value = dual_category_download_request_params
        mocked_serializer_class.return_value = mocked_serializer

        view = DualCategoryDownloadsView()
        request = _build_request(payload=EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD)

        # When
        response = UNWRAPPED_POST(view, request)

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "error_message" in response.data

    @mock.patch(f"{MODULE_PATH}.pivot_dual_category_download_rows")
    def test_pivot_queryset_data_pivots_serialized_rows(
        self,
        mocked_pivot_rows: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given serialized download queryset rows for a dual-category request
        When `_pivot_queryset_data()` is called on `DualCategoryDownloadsView`
        Then the rows are passed to the pivot helper and the pivoted result is returned
        """
        # Given
        mocked_pivot_rows.return_value = [{"age": "00-01", "f": 1.0}]
        view = DualCategoryDownloadsView()
        mocked_serializer = mock.MagicMock()
        mocked_serializer.data = [{"age": "00-01", "sex": "f", "metric_value": 1.0}]
        view._get_serializer_class = mock.MagicMock(return_value=mocked_serializer)

        # When
        result = view._pivot_queryset_data(
            queryset=mock.MagicMock(),
            chart_plot_models=dual_category_download_request_params,
        )

        # Then
        mocked_pivot_rows.assert_called_once_with(
            rows=mocked_serializer.data,
            x_axis="age",
            secondary_category="sex",
        )
        assert result == [{"age": "00-01", "f": 1.0}]

    @mock.patch.object(DualCategoryDownloadsView, "_pivot_queryset_data")
    def test_handle_json_returns_attachment_response(
        self,
        mocked_pivot_queryset_data: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given pivoted dual-category download data
        When `_handle_json()` is called on `DualCategoryDownloadsView`
        Then a JSON attachment response is returned with the pivoted rows
        """
        # Given
        mocked_pivot_queryset_data.return_value = [{"age": "00-01", "f": 1.0}]
        view = DualCategoryDownloadsView()

        # When
        response = view._handle_json(
            queryset=mock.MagicMock(),
            chart_plot_models=dual_category_download_request_params,
        )

        # Then
        assert response.data == [{"age": "00-01", "f": 1.0}]
        assert response["Content-Type"] == "application/json"
        assert "dual_category_download.json" in response["Content-Disposition"]

    @mock.patch(f"{MODULE_PATH}.write_dual_category_data_to_csv")
    @mock.patch(f"{MODULE_PATH}.build_dual_category_csv_headers")
    @mock.patch.object(DualCategoryDownloadsView, "_pivot_queryset_data")
    def test_handle_csv_writes_pivoted_rows(
        self,
        mocked_pivot_queryset_data: mock.MagicMock,
        mocked_build_headers: mock.MagicMock,
        mocked_write_csv: mock.MagicMock,
        dual_category_download_request_params: DualCategoryDownloadRequestParams,
    ):
        """
        Given pivoted dual-category download data
        When `_handle_csv()` is called on `DualCategoryDownloadsView`
        Then CSV headers are built and the pivoted rows are written to a CSV response
        """
        # Given
        mocked_pivot_queryset_data.return_value = [{"age": "00-01", "f": 1.0, "m": 2.0}]
        mocked_build_headers.return_value = ["age", "f", "m"]
        csv_file = mock.MagicMock()
        mocked_write_csv.return_value = csv_file
        view = DualCategoryDownloadsView()

        # When
        response = view._handle_csv(
            queryset=mock.MagicMock(),
            chart_plot_models=dual_category_download_request_params,
        )

        # Then
        mocked_build_headers.assert_called_once_with(
            is_headline=True,
            x_axis="age",
            secondary_category="sex",
            segment_secondary_values=["f", "m"],
        )
        mocked_write_csv.assert_called_once()
        assert response is csv_file
