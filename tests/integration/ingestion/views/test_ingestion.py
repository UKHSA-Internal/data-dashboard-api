from http import HTTPStatus
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

MODULE_PATH = "ingestion.api.views.ingestion"


class TestIngestionView:
    @property
    def path(self) -> str:
        return "/api/ingestion/v1/"

    @pytest.mark.django_db
    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_delegates_call_correctly(
        self, spy_file_ingester: mock.MagicMock, authenticated_api_client: APIClient
    ):
        """
        Given a mocked file
        And an authenticated APIClient
        When the `POST /api/ingestion/v1/` endpoint is hit
        Then the response is a valid HTTP 201 OK
        And the call to handle the business logic is delegated correctly

        Patches:
            `spy_file_ingester`: For the main assertion

        """
        # Given
        mocked_file = mock.MagicMock()

        # When
        response: Response = authenticated_api_client.post(
            path=self.path, data={"file": mocked_file}, format="multipart"
        )

        # Then
        assert response.status_code == HTTPStatus.CREATED.value
        spy_file_ingester.assert_called_once_with(
            file=response.wsgi_request.FILES.get("file")
        )
