from http import HTTPStatus
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

MODULE_PATH = "feedback.api.views.suggestions"


class TestSuggestionsV2View:
    @pytest.mark.django_db
    def test_post_request_returns_correct_response(self):
        """
        Given a valid payload containing a question and answer suggestion
        When the `POST /api/suggestions/v2/` endpoint is hit
        Then an HTTP OK response is returned
        """
        # Given
        path = "/api/suggestions/v2/"
        valid_payload = {
            "how_could_we_improve_your_experience_with_the_dashboard": "",
            "what_would_you_like_to_see_on_the_dashboard_in_the_future": "",
            "did_you_find_everything_you_were_looking_for": "No",
            "what_was_your_reason_for_visiting_the_dashboard_today": "",
        }
        api_client = APIClient()

        # When
        response: Response = api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK.value
