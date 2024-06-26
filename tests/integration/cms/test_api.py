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
    def test_request_returns_draft_with_unpublished_changes(self):
        """
        Given an APIClient
        And a `Page` record which has unpublished changes
        When the detail `GET /api/drafts/{id}/` endpoint is hit
        Then an HTTP 200 OK response is returned
        """
        # Given
        unpublished_title = "Unpublished title"
        page = Page.objects.last()
        page.title = unpublished_title
        # Save a draft but do not publish the change
        page.save_revision()

        api_client = APIClient()

        # When
        response_from_drafts_endpoint: Response = api_client.get(
            path=f"{self.path}/{page.pk}/",
            format="json",
        )
        response_from_pages_endpoint: Response = api_client.get(
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

        # Check the `title` from the `api/drafts/{id}`
        # is the more recent unpublished value
        # and not the older published value
        assert (
            title_field_from_drafts_endpoint
            == unpublished_title
            != title_field_from_pages_endpoint
        )
