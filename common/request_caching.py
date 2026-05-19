"""Support request-scoped cache for per-request cache disablement."""

import contextvars
import logging

"""
If set to True. _disable_request_caching_ctx indicates that we should disable caching for the duration of this request.
"""
_disable_request_caching_ctx: contextvars.ContextVar[bool | None] = (
    contextvars.ContextVar("_request_caching_disabled_ctx", default=None)
)

_logger = logging.getLogger(__name__)


def disable_request_caching():
    _disable_request_caching_ctx.set(True)


def get_request_caching() -> bool | None:
    """Return the request_caching for the current request context.
    Falls back to None.
    """
    request_caching_disabled = _disable_request_caching_ctx.get()
    if isinstance(request_caching_disabled, bool):
        return True  # Disable caching for this request
    return None  # Don't do anything - leave all caching in place


def clear_request_caching() -> None:
    """Clear the request caching for the current request context."""
    _disable_request_caching_ctx.set(None)
