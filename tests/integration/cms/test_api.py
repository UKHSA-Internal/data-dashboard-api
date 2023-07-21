from http import HTTPStatus
from typing import OrderedDict

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient
from wagtail.models import Page

from cms.dashboard.management.commands.build_cms_site import (
    _build_respiratory_viruses_page,
    _build_topic_page,
)
from cms.home.models import HomePage


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
        # Save a draft but do not publish the change
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

        # Check the `title` from the `api/drafts/{id}`
        # is the more recent unpublished value
        # and not the older published value
        assert (
            title_field_from_drafts_endpoint
            == unpublished_title
            != title_field_from_pages_endpoint
        )


class TestListPagesAPI:
    @property
    def path(self) -> str:
        return "/api/pages/"

    @pytest.mark.django_db
    def test_get_request_returns_expected_response(
        self, authenticated_api_client: APIClient
    ):
        """
        Given an APIClient which is authenticated
        And pages which have been created with a parent-child hierarchy in place
        When the list `GET /api/pages/` endpoint is hit
        Then an HTTP 200 OK response is returned
        And the response contains the expected fields
        """
        # Given
        page = Page.objects.first()
        home_page: HomePage = _build_respiratory_viruses_page(parent_page=page)
        _build_topic_page(name="covid_19", parent_page=home_page)

        # When
        response_from_pages_endpoint: Response = authenticated_api_client.get(
            path=self.path,
            format="json",
        )

        # Then
        assert response_from_pages_endpoint.status_code == HTTPStatus.OK

        response_data: OrderedDict = response_from_pages_endpoint.data
        topic_page_from_response: OrderedDict = next(
            item for item in response_data["items"] if item["title"] == "COVID-19"
        )

        # Check that the page is showing its `show_in_menus` attribute
        assert not topic_page_from_response["meta"]["show_in_menus"]

        # Check that the `parent` field is pointing to the data for the correct parent page
        print(topic_page_from_response)

        print(topic_page_from_response["meta"])
        assert topic_page_from_response["meta"]["parent"]["id"] == home_page.id
        assert topic_page_from_response["meta"]["parent"]["title"] == home_page.title
