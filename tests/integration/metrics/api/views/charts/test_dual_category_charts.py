import copy
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.charts.dual_category_charts import (
    EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD,
)
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestChartsView:
    @property
    def path(self) -> str:
        return "/api/charts/dual-category/v1"

    @pytest.mark.parametrize(
        "query_params,response_header",
        [
            ({}, "application/json"),
            ({"preview": False}, "application/json"),
            ({"preview": True}, "image/svg"),
        ],
    )
    @pytest.mark.django_db
    def test_returns_correct_response_for_timeseries_chart(
        self,
        query_params: dict[str, bool],
        response_header: str,
        admin_user: User,
    ):
        """
        Given a valid payload to create a timeseries dual-category chart
        When the `POST /api/charts/dual-category/v1/` endpoint is hit
            with the given preview query params
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        valid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD
        static_fields = valid_payload["static_fields"]

        for age in ("00-04", "05-11"):
            CoreTimeSeriesFactory.create_record(
                topic_name=static_fields["topic"],
                metric_name=static_fields["metric"],
                stratum_name=static_fields["stratum"],
                age_name=age,
                geography_name=static_fields["geography"],
                geography_type_name=static_fields["geography_type"],
                sex=static_fields["sex"],
                date=static_fields["date_from"],
                metric_value=100,
            )

        # When
        response: Response = client.post(
            path=self.path,
            query_params=query_params,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == response_header

    @pytest.mark.django_db
    def test_handles_missing_dates_for_timeseries_chart(
        self,
        admin_user: User,
    ):
        """
        Given a valid payload to create a timeseries dual-category chart
        When the `POST /api/charts/dual-category/v1/` endpoint is hit
            with the given preview query params
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        static_fields = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD["static_fields"]
        valid_payload = copy.deepcopy(EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD)

        for age in ("00-04", "05-11"):
            CoreTimeSeriesFactory.create_record(
                topic_name=static_fields["topic"],
                metric_name=static_fields["metric"],
                stratum_name=static_fields["stratum"],
                age_name=age,
                geography_name=static_fields["geography"],
                geography_type_name=static_fields["geography_type"],
                sex=static_fields["sex"],
                date=static_fields["date_from"],
                metric_value=100,
            )

        valid_payload["static_fields"]["date_from"] = None
        valid_payload["static_fields"]["date_to"] = None
        # When
        response: Response = client.post(
            path=self.path,
            query_params={},
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
