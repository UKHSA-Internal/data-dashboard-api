from http import HTTPStatus
from rest_framework.test import APIClient

from rest_framework.response import Response


class TestSuggestionsView:
    def test_can_hit_endpoint(self, client: APIClient):
        """
        Given a valid payload containing a question and answer suggestion
        When the `POST /api/suggestions/v1/` endpoint is hit
        Then an HTTP OK response is returned
        """
        # Given
        path = "/api/suggestions/v1/"
        valid_payload = {"suggestions": [{"question": "string", "answer": "string"}]}

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            content_type="application/json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK.value
