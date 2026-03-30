import contextvars
import datetime
import logging
import typing as t
from typing import Optional
from django.conf import settings
from django.utils import timezone
from validation.shared import validate_preview_hmac_token

_embargo_time_ctx: contextvars.ContextVar[Optional[datetime.datetime]] = contextvars.ContextVar("embargo_time", default=None)
logger = logging.getLogger(__name__)


class TimeTravelNotSupportedError(Exception):
    pass


TIME_TRAVEL_NOT_SUPPORTED_MESSAGE = '"Time Travel" is not supported on this server.'


def parse_embargo_time_value(embargo_time_value: t.Any) -> Optional[datetime.datetime]:
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
        return datetime.datetime.fromtimestamp(epoch_seconds, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def set_embargo_time(embargo_time_value: object, *, token: str) -> bool:
    """Set embargo time for current request context after validation.

    The value must be either `now` or valid epoch seconds.
    """
    page_previews_enabled = getattr(settings, "PAGE_PREVIEWS_ENABLED", False)
    if not page_previews_enabled:
        _embargo_time_ctx.set(timezone.now())
        logger.error(TIME_TRAVEL_NOT_SUPPORTED_MESSAGE)
        raise TimeTravelNotSupportedError(TIME_TRAVEL_NOT_SUPPORTED_MESSAGE)

    if not validate_preview_hmac_token(token):
        return False

    embargo_time = parse_embargo_time_value(embargo_time_value)
    if embargo_time is None:
        return False

    _embargo_time_ctx.set(embargo_time)
    return True


def get_embargo_time() -> "datetime.datetime":
    """Return the embargo_time for the current request context.
       Falls back to timezone.now().
    """
    embargo_time = _embargo_time_ctx.get()
    if isinstance(embargo_time, datetime.datetime):
        return embargo_time

    return timezone.now()


def clear_embargo_time() -> None:
    """Clear the embargo_time for the current request context."""
    _embargo_time_ctx.set(None)
