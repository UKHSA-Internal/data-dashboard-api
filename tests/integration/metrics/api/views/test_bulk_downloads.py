import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient


class TestBulkDownloadsView:
    def test_get_bulk_downloads_returns_bad_request(
        self,
    ):
        """
        Given an invalid request to the bulk downloads endpoint
        When the `GET /api/bulkdownloads/v1` endpoint is hit
        Then a 400 Bad Request response is received.
        """
        # Given
        client = APIClient()
        path = "/api/bulkdownloads/v1"

        # When
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.django_db
    def test_get_bulk_downloads_returns_zip_file(self):
        """
        Given a valid request to the bulk downloads endpoint.
        When the `GET /api/bulkdownloads/v1` endpoint is hit.
        Then a zip file is returned in the response.
        """
        # Given
        client = APIClient()
        path = "/api/bulkdownloads/v1?file_format=csv"
        fake_date: str = datetime.datetime.now().strftime("%Y-%m-%d")

        # When
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/zip"
        assert (
            response.headers["Content-disposition"]
            == f"attachment; filename=ukhsa_data_dashboard_downloads_{fake_date}.zip"
        )
