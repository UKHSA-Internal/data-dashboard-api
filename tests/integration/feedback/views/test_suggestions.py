from http import HTTPStatus
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from rest_framework.response import Response
from rest_framework.test import APIClient

MODULE_PATH = "feedback.api.views.suggestions"


class TestSuggestionsV2View:
    @property
    def path(self) -> str:
        return "/api/suggestions/v2/"

    @pytest.mark.django_db
    @mock.patch(f"{MODULE_PATH}.send_email")
    def test_post_request_returns_correct_response(
        self,
        mocked_send_email: mock.MagicMock,
        monkeypatch: MonkeyPatch,
    ):
        """
        Given a valid payload containing a question and answer suggestion
        When the `POST /api/suggestions/v2/` endpoint is hit
        Then an HTTP OK response is returned
        """
        # Given
        valid_payload = {
            "how_could_we_improve_your_experience_with_the_dashboard": "",
            "what_would_you_like_to_see_on_the_dashboard_in_the_future": "",
            "did_you_find_everything_you_were_looking_for": "No",
            "what_was_your_reason_for_visiting_the_dashboard_today": "",
        }
        api_client = APIClient()

        # When
        response: Response = api_client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK.value

    @pytest.mark.django_db
    def test_no_recipient_returns_bad_request(self, monkeypatch: MonkeyPatch):
        """
        Given a valid payload containing a question and answer suggestion
        But no `FEEDBACK_EMAIL_RECIPIENT_ADDRESS` env var set
        When the `POST /api/suggestions/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        monkeypatch.delenv("FEEDBACK_EMAIL_RECIPIENT_ADDRESS", raising=False)

        valid_payload = {
            "how_could_we_improve_your_experience_with_the_dashboard": "",
            "what_would_you_like_to_see_on_the_dashboard_in_the_future": "",
            "did_you_find_everything_you_were_looking_for": "No",
            "what_was_your_reason_for_visiting_the_dashboard_today": "",
        }
        api_client = APIClient()

        # When
        response: Response = api_client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST.value
