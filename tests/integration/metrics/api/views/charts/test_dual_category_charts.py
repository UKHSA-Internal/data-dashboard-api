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
        return "/api/dual-category-charts/v1"

    @pytest.mark.django_db
    def test_returns_correct_response_for_age_based_chart(
        self,
        admin_user: User,
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/dual-category-charts/v1/` endpoint is hit
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        valid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD
        for age in ("00-04", "05-11"):
            for sex in ("m", "f"):
                CoreTimeSeriesFactory.create_record(
                    topic_name=valid_payload["static_fields"]["topic"],
                    metric_name=valid_payload["static_fields"]["metric"],
                    stratum_name=valid_payload["static_fields"]["stratum"],
                    age_name=age,
                    geography_name=valid_payload["static_fields"]["geography"],
                    geography_type_name=valid_payload["static_fields"][
                        "geography_type"
                    ],
                    sex=sex,
                )

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"
