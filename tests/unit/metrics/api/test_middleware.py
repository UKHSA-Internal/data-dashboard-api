import datetime
from unittest import mock

from metrics.api.middleware import EmbargoMiddleware

MODULE_PATH = "metrics.api.middleware"


class TestEmbargoMiddleware:
    @mock.patch(f"{MODULE_PATH}.clear_embargo_time")
    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.get_cms_auth_payload")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_sets_embargo_time_when_valid_draft_header_present(
        self,
        spy_validate_token: mock.MagicMock,
        spy_decode_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        spy_clear_embargo_time: mock.MagicMock,
    ):
        request = mock.MagicMock()
        request.path = "/api/pages/1/"
        request.headers = {"x-cms-auth": "Bearer validtoken"}
        spy_validate_token.return_value = True
        spy_decode_token.return_value = {"embargo_time": 1}

        middleware = EmbargoMiddleware(get_response=mock.Mock(return_value={}))
        middleware(request)

        spy_validate_token.assert_called_once_with("validtoken")
        spy_set_embargo_time.assert_called_once_with(
            1,
            token="validtoken",
        )
        assert spy_clear_embargo_time.call_count == 2

    @mock.patch(f"{MODULE_PATH}.clear_embargo_time")
    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_silently_continues_when_header_missing(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        spy_clear_embargo_time: mock.MagicMock,
    ):
        request = mock.MagicMock()
        request.path = "/api/drafts/1/"
        request.headers = {}

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response == {"ok": True}
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()
        assert spy_clear_embargo_time.call_count == 2

    @mock.patch(f"{MODULE_PATH}.clear_embargo_time")
    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_silently_continues_when_token_invalid(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        spy_clear_embargo_time: mock.MagicMock,
    ):
        request = mock.MagicMock()
        request.path = "/api/alerts/v1/heat"
        request.headers = {"x-cms-auth": "Bearer invalidtoken"}
        spy_validate_token.return_value = False

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response.status_code == 401
        assert response.json() == {"detail": "The token was invalid"}
        spy_validate_token.assert_called_once_with("invalidtoken")
        spy_set_embargo_time.assert_not_called()
        assert spy_clear_embargo_time.call_count == 1

    @mock.patch(f"{MODULE_PATH}.clear_embargo_time")
    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_returns_401_when_auth_header_is_not_bearer(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        spy_clear_embargo_time: mock.MagicMock,
    ):
        request = mock.MagicMock()
        request.path = "/api/pages/1/"
        request.headers = {"x-cms-auth": "Token abc"}

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response.status_code == 401
        assert response.json() == {"detail": "The token was invalid"}
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()
        assert spy_clear_embargo_time.call_count == 1

    @mock.patch(f"{MODULE_PATH}.clear_embargo_time")
    @mock.patch(f"{MODULE_PATH}.set_embargo_time")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_skips_non_api_routes_like_cms_admin(
        self,
        spy_validate_token: mock.MagicMock,
        spy_set_embargo_time: mock.MagicMock,
        spy_clear_embargo_time: mock.MagicMock,
    ):
        request = mock.MagicMock()
        request.path = "/cms-admin/pages/123/edit/"
        request.headers = {"x-cms-auth": "Bearer validtoken"}

        get_response = mock.Mock(return_value={"ok": True})
        middleware = EmbargoMiddleware(get_response=get_response)

        response = middleware(request)

        assert response == {"ok": True}
        spy_validate_token.assert_not_called()
        spy_set_embargo_time.assert_not_called()
        assert spy_clear_embargo_time.call_count == 2
