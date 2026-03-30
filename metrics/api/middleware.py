import datetime

from django.http import HttpRequest, HttpResponse

from cms.dashboard.virtual_clock import clear_embargo_time, set_embargo_time
from validation.shared import (
    get_cms_auth_payload,
    get_cms_auth_bearer_token,
    validate_preview_hmac_token,
)

class EmbargoMiddleware:
    """Set request-scoped embargo time when a valid CMS auth token is present.

    Notes:
        - Applies only to custom API request paths (`/api/*`).
        - Invalid/missing headers do not block requests.
        - Context is always cleared after the request completes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Defensive reset in case a worker thread is reused.
        clear_embargo_time()
        if self._is_custom_api_request(request=request):
            self._set_embargo_time_if_header_is_valid(request=request)

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
    def _set_embargo_time_if_header_is_valid(cls, *, request: HttpRequest) -> None:
        token = get_cms_auth_bearer_token(request.headers)
        if token is None:
            return

        is_valid = validate_preview_hmac_token(token)
        if not is_valid:
            return
        
        payload = get_cms_auth_payload(token) or {}

        embargo_time = payload.get("embargo_time")
        if embargo_time is None:
            return

        dt_utc = datetime.datetime.fromtimestamp(
            embargo_time,
            tz=datetime.timezone.utc,
        )
        set_embargo_time(dt_utc)
