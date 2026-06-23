"""Support request-scoped cache for per-request cache disablement."""

import contextvars
import logging
import typing as t

CACHE_CONTROL_HEADER = "Cache-Control"
# we support only one level of disablement and no-store is the most resolute
CACHE_CONTROL_CACHE_DISABLED = "no-store"  # must match exactly


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


def get_cache_control_header(
    headers: t.Mapping[str, str],
) -> str | None:
    """Extract Cache-Control value from the header.
    Returns None if the header is missing.
    All elements in CACHE_CONTROL_HEADER must be matched
             in request header
    Example: CACHE_CONTROL_HEADER = 'private, no-cache'
             cache_control_header = 'no-cache, private'
             This will return True

    """
    cache_control_header = headers.get(CACHE_CONTROL_HEADER, "")

    required = {p.strip() for p in CACHE_CONTROL_CACHE_DISABLED.split(",")}
    actual = {p.strip() for p in cache_control_header.split(",")}

    if not required.issubset(actual):
        return None

    return cache_control_header
