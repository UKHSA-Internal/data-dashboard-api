import pytest
from http import HTTPStatus
from rest_framework.response import Response
from rest_framework.test import APIClient
from wagtail.models import Page
from unittest import mock
from django.utils import timezone
from django.core.signing import dumps
from django.conf import settings


class TestDraftPagesAPI:
    @property
    def path(self) -> str:
        return "/api/drafts"

    @pytest.mark.django_db
    def test_draft_api_always_returns_latest_revision(self):
        """
        Given an APIClient and a Page record in GET /api/pages/{id} which may have unpublished changes
        When the detail GET /api/drafts/{id}/ endpoint is hit
        Then an HTTP 200 OK response is returned and the latest revision (published or draft) is returned
        """
        # Given
        unpublished_title = "Unpublished title"
        page = Page.objects.last()
        page.title = unpublished_title
        # Save a draft but do not publish the change
        page.save_revision()

        api_client = APIClient()

        payload = {
            "page_id": page.id,
            "editor_id": 1,  # Or None, as needed
            "iat": int(timezone.now().timestamp()),
            "exp": int((timezone.now() + timezone.timedelta(seconds=120)).timestamp()),
        }

        token = dumps(payload, salt=settings.PAGE_PREVIEWS_TOKEN_SALT)

        # When
        response_from_drafts_endpoint: Response = api_client.get(
            path=f"{self.path}/{page.id}/",
            HTTP_X_DRAFT_AUTH=f"Bearer {token}",
            format="json",
        )
        response_from_pages_endpoint: Response = api_client.get(
            path=f"/api/pages/{page.id}/",
            format="json",
        )

        # Then
        assert response_from_drafts_endpoint.status_code == HTTPStatus.OK
        assert response_from_pages_endpoint.status_code == HTTPStatus.OK

        # The drafts endpoint should always return the latest revision (published or draft)
        title_field_from_drafts_endpoint: str = response_from_drafts_endpoint.data[
            "title"
        ]
        assert title_field_from_drafts_endpoint == unpublished_title
