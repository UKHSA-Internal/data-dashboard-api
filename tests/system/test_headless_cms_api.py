from collections import OrderedDict

import pytest
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.utils.serializer_helpers import ReturnList


class TestHeadlessCMSAPI:
    @pytest.mark.django_db
    def test_pages_endpoint_responses(self):
        """
        Given the CMS site is built
            via the "build_cms_site" management command
        When the `pages/` API is hit
        Then the correct responses are returned
        """
        # Given
        call_command("build_cms_site")
        api_client = APIClient()

        # When
        path = "/api/pages/"
        response: Response = api_client.get(path=path, format="json")

        # Then
        whats_new_parent_page_data = self._select_page_of_type_from_response(
            response=response, page_type="whats_new.WhatsNewParentPage"
        )
        assert whats_new_parent_page_data["title"] == "What's new"
        whats_new_parent_page_id: int = whats_new_parent_page_data["id"]

        # Grab the ID associated with the `WhatsNewChildPage`
        whats_new_child_page_data = self._select_page_of_type_from_response(
            response=response, page_type="whats_new.WhatsNewChildPage"
        )
        whats_new_child_page_id: int = whats_new_child_page_data["id"]

        # Hit the `pages/{id}/` detail endpoint for the `WhatsNewChildPage`
        path = f"/api/pages/{whats_new_child_page_id}/"
        whats_new_child_page_response: Response = api_client.get(
            path=path, format="json"
        )
        whats_new_child_page_response_data = whats_new_child_page_response.data

        # Check that the correct `badge` associated with the `WhatsNewChildPage`
        assert whats_new_child_page_response_data["badge"]["text"] == "UPDATE"
        assert whats_new_child_page_response_data["badge"]["colour"] == "RED"

        # Check that the `WhatsNewChildPage` is a child of the `WhatsNewParentPage`
        assert (
            whats_new_child_page_response_data["meta"]["parent"]["id"]
            == whats_new_parent_page_id
        )

    @staticmethod
    def _select_page_of_type_from_response(
        response: Response, page_type: str
    ) -> OrderedDict:
        response_data: ReturnList = response.data["items"]
        return next(
            x
            for x in response_data
            if x["meta"]["type"] == page_type
            if isinstance(x, OrderedDict)
        )
