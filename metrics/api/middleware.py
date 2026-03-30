from django.http import HttpRequest, HttpResponse, JsonResponse

from cms.dashboard.virtual_clock import (
    TIME_TRAVEL_NOT_SUPPORTED_MESSAGE,
    TimeTravelNotSupportedError,
    clear_embargo_time,
    set_embargo_time,
)
from validation.shared import (
    CMS_AUTH_HEADER,
    get_cms_auth_bearer_token,
    get_cms_auth_payload,
    validate_preview_hmac_token,
)


class EmbargoMiddleware:
    """Set request-scoped embargo time when a valid CMS auth token is present.

    Notes:
        - Applies only to custom API request paths (`/api/*`).
        - Invalid/missing headers do not block requests.
        - Context is always cleared after the request completes.
    """

    INVALID_TOKEN_DETAIL = {"detail": "The token was invalid"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Defensive reset in case a worker thread is reused.
        clear_embargo_time()
        if self._is_custom_api_request(request=request):
            rejection_response = self._set_embargo_time_if_header_is_valid(
                request=request
            )
            if rejection_response is not None:
                return rejection_response

        try:
            return self.get_response(request)
        finally:
            clear_embargo_time()

    @staticmethod
    def _is_custom_api_request(*, request: HttpRequest) -> bool:
        path_info = getattr(request, "path_info", "")
        path = path_info if isinstance(path_info, str) else getattr(request, "path", "")
        if not isinstance(path, str):
            path = ""
        return path.startswith("/api/")

    @classmethod
    def _set_embargo_time_if_header_is_valid(
        cls, *, request: HttpRequest
    ) -> HttpResponse | None:
        token = get_cms_auth_bearer_token(request.headers)
        if token is None:
            has_auth_header = bool(request.headers.get(CMS_AUTH_HEADER, ""))
            if has_auth_header:
                return JsonResponse(cls.INVALID_TOKEN_DETAIL, status=401)
            return None

        is_valid = validate_preview_hmac_token(token)
        if not is_valid:
            return JsonResponse(cls.INVALID_TOKEN_DETAIL, status=401)

        payload = get_cms_auth_payload(token) or {}

        embargo_time = payload.get("embargo_time")
        if embargo_time is None:
            return None

        try:
            was_set = set_embargo_time(embargo_time, token=token)
        except TimeTravelNotSupportedError:
            return JsonResponse(
                {"detail": TIME_TRAVEL_NOT_SUPPORTED_MESSAGE},
                status=501,
            )
        if not was_set:
            return JsonResponse(cls.INVALID_TOKEN_DETAIL, status=401)

        return None
