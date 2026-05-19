import json
from unittest import mock

from metrics.api.middleware import RequestScopedCachingConfigMiddleware

MODULE_PATH = "metrics.api.middleware"


class TestRequestScopedCachingConfigMiddleware:
    @staticmethod
    def _build_request(*, path: str, headers: dict | None = None, path_info=None):
        request = mock.MagicMock()
        request.path = path
        request.path_info = path if path_info is None else path_info
        request.headers = headers or {}
        return request

    @mock.patch(f"{MODULE_PATH}.disable_request_caching")
    def test_disables_request_caching_when_invalid_header(
        self,
        spy_disable_request_caching: mock.MagicMock,
    ):
        """
        Given a request
        When TestRequestScopedCachingConfigMiddleware processes the request
        Then it must call disable_request_caching
        """
        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
        )
        request.path = object()

        get_response = mock.Mock(return_value={"ok": True})
        middleware = RequestScopedCachingConfigMiddleware(get_response=get_response)

        response = middleware(request)
        RequestScopedCachingConfigMiddleware._set_no_cache_if_header_is_valid(
            request=request
        )

        assert response == {"ok": True}
        assert spy_disable_request_caching.assert_called_once

    @mock.patch(f"{MODULE_PATH}.get_cache_control_header")
    def test_disables_request_caching_when_valid_header(
        self, mock_get_cache_control_header: mock.MagicMock
    ):
        """
        Given a request
        When TestRequestScopedCachingConfigMiddleware processes the request
        Then it must call disable_request_caching
        """
        request = self._build_request(
            path="/api/pages/1/",
            path_info=object(),
        )
        request.path = object()
        mock_get_cache_control_header.return_value = "no-store"

        get_response = mock.Mock(return_value={"ok": True})
        middleware = RequestScopedCachingConfigMiddleware(get_response=get_response)

        response = middleware(request)
        result = RequestScopedCachingConfigMiddleware._set_no_cache_if_header_is_valid(
            request=request
        )

        assert response == {"ok": True}
        assert result is None
