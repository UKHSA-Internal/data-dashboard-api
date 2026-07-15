"""Middleware for establishing request-scoped embargo time on API requests.

This module inspects CMS preview authentication on all custom API routes under
`/api/*`.

Embargo time is set for the lifetime of the current request only when all of
the following are true: the request targets `/api/*`, the CMS auth bearer token
is present and valid, the token payload contains an `embargo_time` value, page
previews are enabled on the server, and the embargo time value can be validated
and applied.

Embargo time is not set when the request is outside `/api/*`, when there is no
CMS auth header, or when a valid preview token does not include an
`embargo_time` value. In those cases the request continues normally and the API
response is generated against the server's current time.

If an auth header is present but invalid, or if the embargo time cannot be
validated and applied, the request is rejected with `401`. If the request asks
for Embargo Time with an `embargo_time` value but the server has page previews
disabled, the request is rejected with `HTTP 501 (Not Implemented)`.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from common.page_previews import (
    CMS_AUTH_HEADER,
    get_cms_auth_bearer_token,
    get_cms_auth_payload,
    validate_preview_hmac_token,
)
from common.request_caching import (
    clear_request_caching,
    disable_request_caching,
    get_cache_control_header,
)
from common.virtual_clock import (
    EMBARGO_TIME_NOT_SUPPORTED_MESSAGE,
    clear_embargo_time,
    set_embargo_time,
)

INVALID_TOKEN_DETAIL = {"detail": "The token was invalid"}


class EmbargoMiddleware:
    """Set request-scoped embargo time when a valid CMS auth token is present.

    Notes:
        - Applies only to custom API request paths (`/api/*`).
        - Invalid/missing headers do not block requests.
        - Context is always cleared after the request completes.
    """

    def __init__(self, get_response):
        """Store the downstream callable for middleware execution."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Apply embargo-time context for eligible API requests before dispatch."""
        try:
            if self._is_custom_api_request(request=request):
                rejection_response = self._set_embargo_time_if_header_is_valid(
                    request=request
                )
                if rejection_response is not None:
                    return rejection_response

            return self.get_response(request)
        finally:
            clear_embargo_time()

    @staticmethod
    def _is_custom_api_request(*, request: HttpRequest) -> bool:
        """Return whether the request targets a custom API route."""
        path_info = getattr(request, "path_info", "")
        path = path_info if isinstance(path_info, str) else getattr(request, "path", "")
        if not isinstance(path, str):
            path = ""
        return path.startswith("/api/")

    @classmethod
    def _set_embargo_time_if_header_is_valid(
        cls, *, request: HttpRequest
    ) -> HttpResponse | None:
        """Validate preview headers and set request-scoped embargo time when allowed."""
        token = get_cms_auth_bearer_token(request.headers)
        if token is None:
            has_auth_header = bool(request.headers.get(CMS_AUTH_HEADER, ""))
            if has_auth_header:
                return JsonResponse(INVALID_TOKEN_DETAIL, status=401)
            return None

        is_valid = validate_preview_hmac_token(token)
        if not is_valid:
            return JsonResponse(INVALID_TOKEN_DETAIL, status=401)

        payload = get_cms_auth_payload(token) or {}

        embargo_time = payload.get("embargo_time")
        if embargo_time is None:
            return None

        if not getattr(settings, "PAGE_PREVIEWS_ENABLED", False):
            return JsonResponse(
                {"detail": EMBARGO_TIME_NOT_SUPPORTED_MESSAGE},
                status=501,
            )

        was_set = set_embargo_time(embargo_time_value=embargo_time, token=token)
        if not was_set:
            return JsonResponse(INVALID_TOKEN_DETAIL, status=401)

        return None


class RequestScopedCachingConfigMiddleware:
    """Set request-scoped caching disabled when Cache-Control no-store HTTP header is present.

    Notes:
        - Applies only to custom API request paths (`/api/*`).
        - Invalid/missing headers do not block requests.
        - Context is always cleared after the request completes.
    """

    def __init__(self, get_response):
        """Store the downstream callable for middleware execution."""
        self.get_response = get_response

    def _handle_preview_request(self, request: HttpRequest, token) -> HttpResponse:
        # response 401 (Unauthorized i.e. not authenticated) if token is invalid
        is_valid = validate_preview_hmac_token(token)
        if not is_valid:
            return JsonResponse(INVALID_TOKEN_DETAIL, status=401)

        if self._is_custom_api_request(request=request):
            self._set_no_cache_if_header_is_valid(request=request)
        return self.get_response(request)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Apply request_no_cache context for eligible API requests before dispatch."""
        try:
            token = get_cms_auth_bearer_token(request.headers)
            # exit if we don't have a token
            if token is None:
                return self.get_response(request)
            return self._handle_preview_request(request, token)
        finally:
            clear_request_caching()

    @staticmethod
    def _is_custom_api_request(*, request: HttpRequest) -> bool:
        """Return whether the request targets a custom API route."""
        path_info = getattr(request, "path_info", "")
        path = path_info if isinstance(path_info, str) else getattr(request, "path", "")
        if not isinstance(path, str):
            path = ""
        return path.startswith("/api/")

    @classmethod
    def _set_no_cache_if_header_is_valid(
        cls, *, request: HttpRequest
    ) -> HttpResponse | None:
        """Validate Cache-Control headers and set request-scoped request_no_cache if allowed."""
        cache_control = get_cache_control_header(request.headers)
        if cache_control is None:
            return None

        disable_request_caching()

        return None
