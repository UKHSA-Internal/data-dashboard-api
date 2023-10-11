from http import HTTPStatus
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

MODULE_PATH = "feedback.api.views.suggestions"


class TestSuggestionsView:
    @mock.patch(f"{MODULE_PATH}.send_email")
    @pytest.mark.django_db
    def test_post_request_returns_correct_response(
        self, spy_send_email: mock.MagicMock
    ):
        """
        Given a valid payload containing a question and answer suggestion
        When the `POST /api/suggestions/v1/` endpoint is hit
        Then an HTTP OK response is returned

        Patches:
            `spy_send_email`: To check the correct function is delegated
                to in order to send the message to the email server.
                And to ensure that the email server
                is not needed for this API test

        """
        # Given
        path = "/api/suggestions/v1/"
        valid_payload = {
            "reason": "I wanted to find out the infection rates of Disease X in my area",
            "improve_experience": "More context around metrics and figures",
            "like_to_see": "I'd like to see more consistency across charts and graphs",
            "did_you_find_everything": "yes",
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
        spy_send_email.assert_called_once_with(suggestions=valid_payload)
