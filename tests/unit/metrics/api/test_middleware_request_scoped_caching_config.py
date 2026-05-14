import json
from unittest import mock

from metrics.api.middleware import RequestScopedCachingConfigMiddleware
from django.http import JsonResponse

MODULE_PATH = "metrics.api.middleware"


class TestRequestScopedCachingConfigMiddleware:
    @staticmethod
    def _build_request(*, path: str, headers: dict | None = None, path_info=None):
        request = mock.MagicMock()
        request.path = path
        request.path_info = path if path_info is None else path_info
        request.headers = headers or {}
        return request

    @mock.patch(f"{MODULE_PATH}.get_cache_control_header")
    @mock.patch(f"{MODULE_PATH}.disable_request_caching")
    def test_set_cache_with_valid_cache_headers_should_disable_cache(
        self, mock_get_cache_control_header, spy_disable_request_caching
    ):
        """
        Given valid Cache-Control headers
        When attempt to disable cache
        Then it should call disable_request_caching and return none
        """

        mock_get_cache_control_header.return_value = None

        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
            headers={"Cache-Control:": "no-store"},
        )

        result = RequestScopedCachingConfigMiddleware._set_no_cache_if_header_is_valid(
            request=request
        )

        spy_disable_request_caching.assert_called_once()
        assert result is None

    @mock.patch(f"{MODULE_PATH}.get_cache_control_header")
    def test_set_cache_with_no_cache_headers_should_return_none(
        self, mock_get_cache_control_header
    ):
        """
        Given no Cache-Control headers
        When attempt to disable cache
        Then it should return none
        """

        mock_get_cache_control_header.return_value = None

        request = self._build_request(
            path="/api/pages/1/", path_info=object(), headers={}
        )

        result = RequestScopedCachingConfigMiddleware._set_no_cache_if_header_is_valid(
            request=request
        )

        assert result is None

    @mock.patch(f"{MODULE_PATH}.get_cms_auth_bearer_token")
    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    @mock.patch(
        f"{MODULE_PATH}.RequestScopedCachingConfigMiddleware._is_custom_api_request"
    )
    @mock.patch(
        f"{MODULE_PATH}.RequestScopedCachingConfigMiddleware._set_no_cache_if_header_is_valid"
    )
    def test_enables_cache_if_valid_api_path(
        self,
        mock_get_cms_auth_bearer_token,
        mock_validate_preview_hmac_token,
        mock_is_custom_api_request,
        mock_set_no_cache_if_header_is_valid,
    ):
        """
        Given valid API path
        When RequestScopedCachingConfigMiddleware
        Then it should disable the cache
        """

        mock_get_cms_auth_bearer_token.return_value = "valid token"
        mock_validate_preview_hmac_token.return_value = True
        mock_is_custom_api_request.return_value = True

        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
            headers={"x-cms-auth": "Bearer valid-HMAC-token"},
        )

        get_response = mock.Mock(return_value={"ok": True})
        middleware = RequestScopedCachingConfigMiddleware(get_response=get_response)
        response = middleware(request)

        assert response == {"ok": True}
        mock_set_no_cache_if_header_is_valid.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    @mock.patch(
        f"{MODULE_PATH}.RequestScopedCachingConfigMiddleware._set_no_cache_if_header_is_valid"
    )
    def test_is_custom_api_request_calls_set_no_cache(
        self, mock_validate_preview_hmac_token, spy__set_no_cache_if_header_is_valid
    ):
        """
        Given a request
            with valid token
            with valid api path
        When TestRequestScopedCachingConfigMiddleware
        Then it must call _set_no_cache_if_header_is_valid
        """

        mock_validate_preview_hmac_token.return_value = True

        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
            headers={"x-cms-auth": "Bearer valid-HMAC-token"},
        )

        request.path = object()
        get_response = mock.Mock(return_value={"ok": True})
        middleware = RequestScopedCachingConfigMiddleware(get_response=get_response)

        # When
        response = middleware(request)

        # Then
        spy__set_no_cache_if_header_is_valid.assert_called_once
        assert response == {"ok": True}

    @mock.patch(f"{MODULE_PATH}.validate_preview_hmac_token")
    def test_invalid_token_returns_401(self, mock_validate_preview_hmac_token):
        """
        Given a request
            with invalid token
        When TestRequestScopedCachingConfigMiddleware
        Then it must return 401 (Unauthorized)
        """

        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
            headers={"x-cms-auth": "Bearer invalid-HMAC-token"},
        )

        mock_validate_preview_hmac_token.return_value = False

        request.path = object()
        get_response = mock.Mock(return_value={"ok": True})
        middleware = RequestScopedCachingConfigMiddleware(get_response=get_response)

        # When
        response = middleware(request)

        # Then
        assert response.status_code == 401
        assert isinstance(response, JsonResponse)

    def test_no_token_returns_ok(self):
        """
        Given a request with no token
        When TestRequestScopedCachingConfigMiddleware
        Then it must return OK
        """

        # Given ruquest without header (no token)
        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
        )
        request.path = object()
        get_response = mock.Mock(return_value={"ok": True})
        middleware = RequestScopedCachingConfigMiddleware(get_response=get_response)

        # When
        response = middleware(request)

        # Then
        assert response == {"ok": True}
