"""Support request-scoped "Embargo Date" for embargoed data views.

This module provides a virtual clock that allows authorised preview users to
view data as if the current time were set to the future (or past).
It is used to support embargo previews, by enabling the consumer to view data
that is presently restricted.
"""

import contextvars
import logging
from datetime import datetime, UTC
from typing import Any

from django.conf import settings
from django.utils import timezone

from common.page_previews import validate_preview_hmac_token

_embargo_time_ctx: contextvars.ContextVar[datetime | None] = contextvars.ContextVar(
    "embargo_time", default=None
)
_logger = logging.getLogger(__name__)


class EmbargoDateNotSupportedError(Exception):
    """Raised when preview Embargo Date is requested on a server that disables it."""


EMBARGO_DATE_NOT_SUPPORTED_MESSAGE = '"Embargo Date" is not supported on this server.'


def parse_embargo_time_value(embargo_time_value: Any) -> datetime | None:
    """Parse embargo time value into a timezone-aware datetime.

    Accepted values:
        - "now" (case-insensitive)
        - Unix epoch seconds as string/int/float
    """
    if isinstance(embargo_time_value, str):
        candidate = embargo_time_value.strip()
        if candidate.lower() == "now":
            return timezone.now()
        try:
            epoch_seconds = int(candidate)
        except (TypeError, ValueError):
            return None
    elif isinstance(embargo_time_value, (int, float)) and not isinstance(
        embargo_time_value, bool
    ):
        epoch_seconds = int(embargo_time_value)
    else:
        return None

    try:
        return datetime.fromtimestamp(epoch_seconds, tz=UTC)
    except (OverflowError, OSError, ValueError):
        return None


def set_embargo_time(*, embargo_time_value: object, token: str) -> bool:
    """Set embargo time for current request context after validation.

    The value must be either `now` or valid epoch seconds.
    """
    page_previews_enabled = getattr(settings, "PAGE_PREVIEWS_ENABLED", False)
    if not page_previews_enabled:
        _embargo_time_ctx.set(None)
        _logger.error(EMBARGO_DATE_NOT_SUPPORTED_MESSAGE)
        raise EmbargoDateNotSupportedError(EMBARGO_DATE_NOT_SUPPORTED_MESSAGE)

    if not validate_preview_hmac_token(token):
        return False

    embargo_time = parse_embargo_time_value(embargo_time_value)
    if embargo_time is None:
        return False

    _embargo_time_ctx.set(embargo_time)
    return True


def get_embargo_time() -> datetime:
    """Return the embargo_time for the current request context.
    Falls back to timezone.now().
    """
    embargo_time = _embargo_time_ctx.get()
    if isinstance(embargo_time, datetime):
        return embargo_time

    return timezone.now()


def clear_embargo_time() -> None:
    """Clear the embargo_time for the current request context."""
    _embargo_time_ctx.set(None)
