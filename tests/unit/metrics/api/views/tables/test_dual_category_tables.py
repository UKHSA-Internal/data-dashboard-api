from http import HTTPStatus
from unittest import mock

import pytest

from metrics.api.views.tables.dual_category_tables import DualCategoryTablesView
from metrics.domain.models.tables.dual_category import DualCategoryTableRequestParams
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)

MODULE_PATH = "metrics.api.views.tables.dual_category_tables"


class TestDualCategoryTablesView:
    @pytest.mark.parametrize(
        "exception",
        [DataNotFoundForAnyPlotError(), InvalidPlotParametersError()],
    )
    @mock.patch("metrics.api.decorators.auth.auth.AUTH_ENABLED", False)
    @mock.patch(f"{MODULE_PATH}.access.generate_table_for_full_plots")
    @mock.patch(f"{MODULE_PATH}.DualCategoryTableRequestParamsSerializer")
    def test_post_returns_bad_request_when_table_generation_fails(
        self,
        mocked_serializer_class: mock.MagicMock,
        mocked_generate_table: mock.MagicMock,
        exception: Exception,
    ):
        """
        Given a dual-category table generation fails
        When `post()` is called on `DualCategoryTablesView`
        Then a `400 Bad Request` response is returned with an error message
        """
        # Given
        mocked_serializer = mock.MagicMock()
        mocked_serializer_class.return_value = mocked_serializer
        mocked_serializer.to_models.return_value = mock.MagicMock(
            spec=DualCategoryTableRequestParams
        )
        mocked_generate_table.side_effect = exception

        # When
        response = DualCategoryTablesView.post(request=mock.MagicMock())

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data == {"error_message": str(exception)}
