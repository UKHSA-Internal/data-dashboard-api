from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.factories.cms.snippets.menu import MenuFactory, SimpleMenuFactory


class TestMenuView:
    @property
    def path(self) -> str:
        return "/api/menus/v1"

    @pytest.mark.django_db
    def test_get_request_returns_correct_data(self):
        """
        Given an active `Menu` record
        When a GET request is made to the `/api/menus/v1` endpoint
        Then the response is a valid HTTP OK with the correct data
        """
        # Given
        client = APIClient()
        active_menu_body = [
            {
                "type": "row",
                "value": {
                    "columns": [
                        {
                            "type": "column",
                            "value": {
                                "heading": "",
                                "links": {
                                    "primary_link": {
                                        "title": "COVID-19",
                                        "body": "",
                                        "page": 4,
                                        "html_url": "https://my-prefix.dev.ukhsa-dashboard.data.gov.uk/topics/covid-19",
                                    },
                                    "secondary_links": [],
                                },
                            },
                            "id": "6dcfe146-67a4-40a8-b41c-bd95a2bc449a",
                        }
                    ]
                },
                "id": "aa57931b-d683-4875-85a6-921852dcc5b3",
            }
        ]
        MenuFactory.create(
            body=active_menu_body, is_active=True, internal_label="Test menu design"
        )
        inactive_menu = MenuFactory.create(
            body=[], is_active=False, internal_label="Test menu design"
        )

        # When
        response: Response = client.get(
            path=self.path,
            format="json",
            headers={"Cache-Force-Refresh": True},
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert (
            response.data["active_menu"]
            == active_menu_body
            != inactive_menu.body.get_prep_value()
        )


class TestSimpleMenuView:
    @property
    def path(self) -> str:
        return "/api/menus/v2"

    @pytest.mark.django_db
    def test_get_request_returns_correct_data(self):
        """
        Given an active `SimpleMenu` record
        When a GET request is made to the `/api/menus/v2` endpoint
        Then the response is a valid HTTP OK with the correct data
        """
        # Given
        client = APIClient()
        active_menu_body = [
            {
                "type": "link",
                "value": {
                    "title": "What's coming",
                    "page": 3,
                    "html_url": "https://my-prefix.dev.ukhsa-dashboard.data.gov.uk/whats-coming/",
                },
                "id": "d8e270c7-f3d7-41cf-8d7c-c2bbe62ed71d",
            },
            {
                "type": "link",
                "value": {
                    "title": "What's new",
                    "page": 14,
                    "html_url": "https://my-prefix.dev.ukhsa-dashboard.data.gov.uk/whats-new/",
                },
                "id": "021352b9-d606-48ee-b942-1739ccec9e03",
            },
        ]
        SimpleMenuFactory.create(
            body=active_menu_body, is_active=True, internal_label="Test simple design"
        )
        inactive_menu = MenuFactory.create(
            body=[], is_active=False, internal_label="Test simple design"
        )

        # When
        response: Response = client.get(
            path=self.path,
            format="json",
            headers={"Cache-Force-Refresh": True},
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert (
            response.data["active_menu"]
            == active_menu_body
            != inactive_menu.body.get_prep_value()
        )
