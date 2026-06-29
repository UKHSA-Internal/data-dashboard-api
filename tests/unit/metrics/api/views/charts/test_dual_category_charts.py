from http import HTTPStatus
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from django.http import FileResponse
from rest_framework import permissions
from rest_framework.response import Response

import config
from metrics.api.views.charts.dual_category_charts import DualCategoryChartsView
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
)
from metrics.interfaces.charts.common.generation import ChartResult
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)


class TestDualCategoryChartsView:
    def test_authentication_is_required(self, monkeypatch: MonkeyPatch):
        """
        Given a `DualCategoryChartsView` object
        When `get_permission()` is called
        Then there is a permissions restriction of `IsAuthenticated`
        """
        # Given
        with monkeypatch.context() as m:
            m.setattr(target=config, name="APP_MODE", value="CMS_ADMIN")
            dual_category_charts_view = DualCategoryChartsView()

            # When
            permissions_on_view = dual_category_charts_view.get_permissions()

        # Then
        assert type(permissions_on_view[0]) is permissions.IsAuthenticated


class TestDualCategoryChartsViewErrorHandling:
    @pytest.mark.parametrize(
        "exception",
        [DataNotFoundForAnyPlotError(), InvalidPlotParametersError()],
    )
    @mock.patch(
        "metrics.api.views.charts.dual_category_charts.generate_chart_as_file",
    )
    def test_handle_chart_as_file_returns_bad_request_when_chart_generation_fails(
        self,
        mocked_generate_chart_as_file: mock.MagicMock,
        exception: Exception,
    ):
        """
        Given chart generation raises a plot error
        When `_handle_chart_as_file()` is called
        Then an HTTP 400 response with the error message is returned
        """
        # Given
        mocked_generate_chart_as_file.side_effect = exception
        chart_request_params = mock.MagicMock(spec=DualCategoryChartRequestParams)

        # When
        response = DualCategoryChartsView._handle_chart_as_file(
            chart_request_params=chart_request_params,
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data == {"error_message": str(exception)}

    @pytest.mark.parametrize(
        "exception",
        [DataNotFoundForAnyPlotError(), InvalidPlotParametersError()],
    )
    @mock.patch(
        "metrics.api.views.charts.dual_category_charts.generate_encoded_chart",
    )
    def test_handle_encoded_svg_returns_bad_request_when_chart_generation_fails(
        self,
        mocked_generate_encoded_chart: mock.MagicMock,
        exception: Exception,
    ):
        """
        Given chart generation raises a plot error
        When `_handle_encoded_svg()` is called
        Then an HTTP 400 response with the error message is returned
        """
        # Given
        mocked_generate_encoded_chart.side_effect = exception
        chart_request_params = mock.MagicMock(spec=DualCategoryChartRequestParams)

        # When
        response = DualCategoryChartsView._handle_encoded_svg(
            chart_request_params=chart_request_params,
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data == {"error_message": str(exception)}


class TestDualCategoryChartsViewSuccessHandling:
    @mock.patch(
        "metrics.api.views.charts.dual_category_charts.generate_chart_as_file",
    )
    def test_handle_chart_as_file_returns_file_response_when_chart_generation_succeeds(
        self,
        mocked_generate_chart_as_file: mock.MagicMock,
    ):
        """
        Given chart generation succeeds
        When `_handle_chart_as_file()` is called
        Then a `FileResponse` containing the chart image is returned
        """
        # Given
        mocked_generate_chart_as_file.return_value = b"<svg></svg>"
        chart_request_params = mock.MagicMock(spec=DualCategoryChartRequestParams)
        chart_request_params.file_format = "svg"

        # When
        response = DualCategoryChartsView._handle_chart_as_file(
            chart_request_params=chart_request_params,
        )

        # Then
        assert isinstance(response, FileResponse)
        assert response.getvalue() == b"<svg></svg>"
        assert response.headers["Content-Type"] == "image/svg"

    @mock.patch(
        "metrics.api.views.charts.dual_category_charts.generate_encoded_chart",
    )
    def test_handle_encoded_svg_returns_response_when_chart_generation_succeeds(
        self,
        mocked_generate_encoded_chart: mock.MagicMock,
    ):
        """
        Given chart generation succeeds
        When `_handle_encoded_svg()` is called
        Then an HTTP 200 response containing the encoded chart is returned
        """
        # Given
        mocked_generate_encoded_chart.return_value = ChartResult(
            last_updated="2024-01-01",
            chart="encoded-svg",
            alt_text="Chart description",
            figure={},
        )
        chart_request_params = mock.MagicMock(spec=DualCategoryChartRequestParams)

        # When
        response = DualCategoryChartsView._handle_encoded_svg(
            chart_request_params=chart_request_params,
        )

        # Then
        assert isinstance(response, Response)
        assert response.status_code == HTTPStatus.OK
        assert response.data["chart"] == "encoded-svg"
