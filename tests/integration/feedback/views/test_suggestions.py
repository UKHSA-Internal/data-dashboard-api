from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient


class TestSuggestionsView:
    @pytest.mark.django_db
    def test_post_request_returns_correct_response(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload containing a question and answer suggestion
        When the `POST /api/suggestions/v1/` endpoint is hit
        Then an HTTP OK response is returned
        """
        # Given
        path = "/api/suggestions/v1/"
        valid_payload = {
            "reason": "I wanted to find out the infection rates of Disease X in my area",
            "improve_experience": "More context around metrics and figures",
            "like_to_see": "I'd like to see more consistency across charts and graphs",
            "did_you_find_everything": "yes",
        }

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK.value
