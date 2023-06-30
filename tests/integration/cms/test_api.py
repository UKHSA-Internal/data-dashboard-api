from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient
from wagtail.models import Page


class TestDraftPagesAPI:
    @property
    def path(self) -> str:
        return "/api/drafts"

    @pytest.mark.django_db
    def test_request_returns_draft_with_unpublished_changes(
        self, authenticated_api_client: APIClient
    ):
        """
        Given an APIClient which is authenticated
        And a `Page` record which has unpublished changes
        When the detail `GET /api/drafts/{id}/` endpoint is hit
        Then an HTTP 200 OK response is returned
        """
        # Given
        unpublished_title = "Unpublished title"
        page = Page.objects.last()
        page.title = unpublished_title
        page.save_revision()

        # When
        response_from_drafts_endpoint: Response = authenticated_api_client.get(
            path=f"{self.path}/{page.pk}/",
            format="json",
        )
        response_from_pages_endpoint: Response = authenticated_api_client.get(
            path=f"/api/pages/{page.pk}/",
            format="json",
        )

        # Then
        assert response_from_drafts_endpoint.status_code == HTTPStatus.OK
        assert response_from_pages_endpoint.status_code == HTTPStatus.OK

        # Get the more recent unpublished `title` from the `api/drafts/{id}` response
        title_field_from_drafts_endpoint: str = response_from_drafts_endpoint.data[
            "title"
        ]
        # Get the outdated but published `title` from the `api/pages/{id}` response
        title_field_from_pages_endpoint: str = response_from_pages_endpoint.data[
            "title"
        ]

        assert (
            title_field_from_drafts_endpoint
            == unpublished_title
            != title_field_from_pages_endpoint
        )

    @pytest.mark.django_db
    def test_request_without_api_key_is_unauthorized(self):
        """
        Given an APIClient which is not authenticated
        When the `GET /api/drafts/{id}/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.get(path=f"{self.path}/1/", data={})

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
