import inspect
from http import HTTPStatus
from unittest import mock

import pytest

from metrics.api.views.downloads import (
    SingleCategoryDownloadsView,
    EXAMPLE_SINGLE_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD,
)

from metrics.domain.models import ChartRequestParams

from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)

MODULE_PATH = "metrics.api.views.downloads.single_category_downloads"
UNWRAPPED_POST = inspect.unwrap(SingleCategoryDownloadsView.post)


def _build_request(*, payload: dict) -> mock.MagicMock:
    request = mock.MagicMock()
    request.data = payload
    return request


class TestDownloadsView:
    def test_get_serializer_raises_error(self):
        """
        Given an invalid `metric_group`
        When the `_get_serializer_class()` method is called.
        Then a `ValueError` is raised
        """
        # Given
        downloads_view = SingleCategoryDownloadsView()
        invalid_metric_group = "invalid_metric_group"

        # When / Then
        with pytest.raises(ValueError):
            downloads_view._get_serializer_class(
                queryset=mock.MagicMock(),
                metric_group=invalid_metric_group,
            )

    @pytest.mark.parametrize(
        "exception",
        [
            pytest.param(
                DataNotFoundForAnyPlotError(), id="DataNotFoundForAnyPlotError"
            ),
            pytest.param(InvalidPlotParametersError(), id="InvalidPlotParametersError"),
        ],
    )
    @mock.patch(f"{MODULE_PATH}.SingleCategoryDownloadsSerializer")
    @mock.patch(f"{MODULE_PATH}.access.get_downloads_data")
    def test_post_returns_bad_request_when_error_raised(
        self,
        mocked_get_downloads_data: mock.MagicMock,
        mocked_serializer_class: mock.MagicMock,
        fake_chart_request_params: ChartRequestParams,
        exception: Exception,
    ):
        """
        Given a single-category download request where no plot data is found or incorrect data is provided
        When `post()` is called on `SingleCategoryDownloadsView`
        Then a `400 Bad Request` response is returned with an error message
        """
        # Given
        mocked_get_downloads_data.side_effect = exception
        mocked_serializer = mock.MagicMock()
        mocked_serializer.data = {"file_format": "json"}
        mocked_serializer.to_models.return_value = fake_chart_request_params
        mocked_serializer_class.return_value = mocked_serializer

        view = SingleCategoryDownloadsView()
        request = _build_request(
            payload=EXAMPLE_SINGLE_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD
        )

        # When
        response = UNWRAPPED_POST(view, request)

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "error_message" in response.data
