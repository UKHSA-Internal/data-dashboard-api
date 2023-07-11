from http import HTTPStatus
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient


class TestFileUploadView:
    @pytest.mark.django_db
    @mock.patch("metrics.api.views.file_upload.load_core_data")
    def test_get_returns_correct_response(
        self,
        mocked_load_core_data: mock.MagicMock,
        authenticated_api_client: APIClient,
    ):
        """
        Given an authenticated APIClient
        When the `PUT /api/upload/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED

        Patches:
            `mocked_load_core_data`: To remove the side
                effect of uploading the data from the file

        """
        # Given
        path = "/api/upload/"

        # When
        response: Response = authenticated_api_client.put(path=path)

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED

    @pytest.mark.django_db
    def test_get_request_without_api_key_is_unauthorized(
        self, authenticated_api_client: APIClient
    ):
        """
        Given an APIClient which is not authenticated
        When the `PUT /api/upload/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()
        path = "/api/upload/"

        # When
        response: Response = client.put(path=path)

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
