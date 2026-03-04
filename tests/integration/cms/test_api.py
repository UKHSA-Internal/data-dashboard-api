from http import HTTPStatus

import pytest
from django.core.signing import dumps
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient
from wagtail.models import Page, Site
from wagtail.models.i18n import Locale

from cms.common.models import CommonPage


class TestDraftPagesAPI:
    @property
    def path(self) -> str:
        return "/api/drafts"

    @staticmethod
    def _build_preview_auth_header(*, page_id: int) -> dict[str, str]:
        now = timezone.now()
        token = dumps(
            {
                "page_id": page_id,
                "iat": int(now.timestamp()),
                "exp": int((now.timestamp()) + 120),
            },
            salt="preview-token",
        )
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    @pytest.mark.django_db
    def test_draft_preview_returns_draft_with_unpublished_changes(self):
        """
        Given an APIClient
        And a `Page` record which has unpublished changes
        When the detail `GET /api/drafts/{slug}/` endpoint is hit
        Then an HTTP 200 OK response is returned
        """
        # Given
        # Create a locale and root page for the test
        Locale.objects.get_or_create(language_code="en")
        root = Page.get_first_root_node() or Page.add_root(title="Root", slug="root")

        # Create or update the Site for the root page
        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": root, "site_name": "Test Site"},
        )
        # Ensure the site points to our root page
        site.root_page = root
        site.is_default_site = True
        site.save()

        # Create a CommonPage and publish it
        original_title = "Original published title"
        page = CommonPage(
            title=original_title,
            slug="test-preview-page",
            body="Test page body content",
            seo_title="Test Page",
        )
        root.add_child(instance=page)
        page.save_revision().publish()

        # Make unpublished changes to the page
        unpublished_title = "Unpublished title"
        page.title = unpublished_title
        # Save a draft but do not publish the change
        page.save_revision()

        api_client = APIClient()
        authorization_header = self._build_preview_auth_header(page_id=page.pk)

        # When
        response_from_drafts_endpoint: Response = api_client.get(
            path=f"{self.path}/{page.slug}/",
            format="json",
            **authorization_header,
        )
        response_from_pages_endpoint: Response = api_client.get(
            path=f"/api/pages/{page.pk}/",
            format="json",
        )

        # Then
        assert response_from_drafts_endpoint.status_code == HTTPStatus.OK
        assert response_from_pages_endpoint.status_code == HTTPStatus.OK

        # Get the more recent unpublished `title` from the `api/drafts/{slug}` response
        title_field_from_drafts_endpoint: str = response_from_drafts_endpoint.data[
            "title"
        ]
        # Get the outdated but published `title` from the `api/pages/{id}` response
        title_field_from_pages_endpoint: str = response_from_pages_endpoint.data[
            "title"
        ]

        # Check the `title` from the `api/drafts/{slug}`
        # is the more recent unpublished value
        # and not the older published value
        assert (
            title_field_from_drafts_endpoint
            == unpublished_title
            != title_field_from_pages_endpoint
        )

        draft_meta = response_from_drafts_endpoint.data["meta"]
        page_meta = response_from_pages_endpoint.data["meta"]
        assert draft_meta["type"] == page_meta["type"]
        assert draft_meta["type"] is not None
        assert draft_meta["detail_url"] == page_meta["detail_url"]
        assert draft_meta["detail_url"] is not None
        assert draft_meta["parent"] == page_meta["parent"]
        assert draft_meta["alias_of"] == page_meta["alias_of"]

    @pytest.mark.django_db
    def test_draft_preview_accepts_nested_route_slug_path(self):
        """
        Given a nested page route and unpublished changes on the child page
        When `GET /api/drafts/{route-slug}/` is called with a valid preview token
        Then HTTP 200 is returned with draft content using the same schema shape
        """
        # Given
        Locale.objects.get_or_create(language_code="en")
        root = Page.get_first_root_node() or Page.add_root(title="Root", slug="root")

        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": root, "site_name": "Test Site"},
        )
        site.root_page = root
        site.is_default_site = True
        site.save()

        parent = Page(title="Respiratory viruses", slug="respiratory-viruses")
        root.add_child(instance=parent)
        parent.save_revision().publish()

        child = Page(title="COVID-19", slug="covid-19")
        parent.add_child(instance=child)
        child.save_revision().publish()

        child.title = "COVID-19 draft"
        child.save_revision()

        api_client = APIClient()
        authorization_header = self._build_preview_auth_header(page_id=child.pk)

        nested_route_slug = "respiratory-viruses/covid-19"

        # When
        response_from_drafts_endpoint: Response = api_client.get(
            path=f"{self.path}/{nested_route_slug}/",
            format="json",
            **authorization_header,
        )
        response_from_pages_endpoint: Response = api_client.get(
            path=f"/api/pages/{child.pk}/",
            format="json",
        )

        # Then
        assert response_from_drafts_endpoint.status_code == HTTPStatus.OK
        assert response_from_pages_endpoint.status_code == HTTPStatus.OK
        assert response_from_drafts_endpoint.data["id"] == child.pk

        draft_meta = response_from_drafts_endpoint.data["meta"]
        page_meta = response_from_pages_endpoint.data["meta"]
        assert draft_meta["type"] == page_meta["type"]
        assert draft_meta["detail_url"] == page_meta["detail_url"]
        assert draft_meta["parent"] == page_meta["parent"]
        assert draft_meta["alias_of"] == page_meta["alias_of"]
