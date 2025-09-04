from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.tables.subplot_tables.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)


class TestTablesSubplotView:
    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(self):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/subplot/v1` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        valid_payload = REQUEST_PAYLOAD_EXAMPLE
        path = "/api/tables/subplot/v1"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK
