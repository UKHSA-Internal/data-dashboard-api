import json
from unittest import mock

from metrics.api.middleware.preview import EmbargoMiddleware

MODULE_PATH = "metrics.api.middleware.preview"


class TestEmbargoMiddleware:
    @staticmethod
    def _build_request(*, path: str, headers: dict | None = None, path_info=None):
        request = mock.MagicMock()
        request.path = path
        request.path_info = path if path_info is None else path_info
        request.headers = headers or {}
        return request

    @staticmethod
    def _assert_invalid_token_response(response) -> None:
        assert response.status_code == 401
        assert json.loads(response.content) == {"detail": "The token was invalid"}

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_skips_request_when_path_is_not_a_string(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
    ):
        """
        Given a request whose path values are not strings
        When EmbargoMiddleware processes the request
        Then it bypasses token validation and embargo assignment
        """
        request = self._build_request(
            path="/api/pages/1/",
            headers={"x-cms-auth": "Bearer validtoken"},
            path_info=object(),
        )
        request.path = object()

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response == {"ok": True}
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.get_cms_auth_payload")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_sets_embargo_time_when_valid_draft_header_present(
        self,
        spy_validate_token: mock.MagicMock,
        spy_decode_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        settings,
    ):
        """
        Given a request with a valid bearer token and embargo_time in payload
        When EmbargoMiddleware processes the request
        Then it validates the token and sets embargo time on the request context
        """
        request = self._build_request(
            path="/api/pages/1/",
            headers={"x-cms-auth": "Bearer validtoken"},
        )
        settings.PAGE_PREVIEWS_ENABLED = True
        spy_validate_token.return_value = True
        spy_decode_token.return_value = {"embargo_time": 1}

        middleware = EmbargoMiddleware(get_response=mock.Mock(return_value={}))
        middleware(request)

        spy_validate_token.assert_called_once_with("validtoken")
        spy_set_embargo_time.assert_called_once_with(
            embargo_time_value=1,
            token="validtoken",
        )

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_silently_continues_when_header_missing(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
    ):
        """
        Given a drafts request with no auth header
        When EmbargoMiddleware processes the request
        Then it continues without validation and without setting embargo time
        """
        request = self._build_request(path="/api/drafts/1/")

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response == {"ok": True}
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.get_cms_auth_payload")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_silently_continues_when_valid_token_has_no_embargo_time(
        self,
        spy_validate_token: mock.MagicMock,
        spy_decode_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
    ):
        """
        Given a drafts request with a valid token but no embargo_time claim
        When EmbargoMiddleware processes the request
        Then it continues and does not set embargo time
        """
        request = self._build_request(
            path="/api/drafts/1/",
            headers={"x-cms-auth": "Bearer validtoken"},
        )
        spy_validate_token.return_value = True
        spy_decode_token.return_value = {}

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response == {"ok": True}
        spy_validate_token.assert_called_once_with("validtoken")
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_silently_continues_when_token_invalid(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
    ):
        """
        Given an API request with an invalid bearer token
        When EmbargoMiddleware processes the request
        Then it returns an invalid-token 401 response
        """
        request = self._build_request(
            path="/api/alerts/v1/heat",
            headers={"x-cms-auth": "Bearer invalidtoken"},
        )
        spy_validate_token.return_value = False

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        self._assert_invalid_token_response(response)
        spy_validate_token.assert_called_once_with("invalidtoken")
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_returns_401_when_auth_header_is_not_bearer(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
    ):
        """
        Given an API request whose auth header is not Bearer format
        When EmbargoMiddleware processes the request
        Then it returns an invalid-token 401 response
        """
        request = self._build_request(
            path="/api/pages/1/",
            headers={"x-cms-auth": "Token abc"},
        )

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        self._assert_invalid_token_response(response)
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_skips_non_api_routes_like_cms_admin(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
    ):
        """
        Given a non-API route under cms-admin
        When EmbargoMiddleware processes the request
        Then it skips token validation and embargo assignment
        """
        request = self._build_request(
            path="/cms-admin/pages/123/edit/",
            headers={"x-cms-auth": "Bearer validtoken"},
        )

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response == {"ok": True}
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.get_cms_auth_payload")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_returns_501_when_embargo_date_is_not_supported(
        self,
        spy_validate_token: mock.MagicMock,
        spy_decode_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        settings,
    ):
        """
        Given a valid token containing embargo_time while previews are disabled
        When EmbargoMiddleware processes the request
        Then it returns a 501 response indicating Embargo Time is unsupported
        """
        request = self._build_request(
            path="/api/pages/1/",
            headers={"x-cms-auth": "Bearer validtoken"},
        )
        settings.PAGE_PREVIEWS_ENABLED = False
        spy_validate_token.return_value = True
        spy_decode_token.return_value = {"embargo_time": 1}

        middleware = EmbargoMiddleware(get_response=mock.Mock(return_value={}))

        response = middleware(request)

        assert response.status_code == 501
        assert json.loads(response.content) == {
            "detail": '"Embargo Time" is not supported on this server.'
        }
        spy_set_embargo_time.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.set_embargo_time", return_value=False)
    @mock.patch(f"{MODULE_PATH}.get_cms_auth_payload")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_returns_401_when_embargo_time_is_rejected(
        self,
        spy_validate_token: mock.MagicMock,
        spy_decode_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        settings,
    ):
        """
        Given a valid token with embargo_time that is rejected by set_embargo_time
        When EmbargoMiddleware processes the request
        Then it returns an invalid-token 401 response
        """
        request = self._build_request(
            path="/api/pages/1/",
            headers={"x-cms-auth": "Bearer validtoken"},
        )
        settings.PAGE_PREVIEWS_ENABLED = True
        spy_validate_token.return_value = True
        spy_decode_token.return_value = {"embargo_time": 1}

        middleware = EmbargoMiddleware(get_response=mock.Mock(return_value={}))

        response = middleware(request)

        self._assert_invalid_token_response(response)
        spy_set_embargo_time.assert_called_once_with(
            embargo_time_value=1, token="validtoken"
        )
