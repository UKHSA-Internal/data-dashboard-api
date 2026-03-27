import contextvars
import datetime
from typing import Optional
import datetime
from django.utils import timezone

_embargo_time_ctx: contextvars.ContextVar[Optional[datetime.datetime]] = contextvars.ContextVar("embargo_time", default=None)


def set_embargo_time(embargo_time: "datetime.datetime") -> None:
    """Set the embargo_time for the current request context"""
    _embargo_time_ctx.set(embargo_time)


def get_embargo_time() -> "datetime.datetime":
    """Return the embargo_time for the current request context.
       Falls back to timezone.now().
    """
    embargo_time = _embargo_time_ctx.get()
    if embargo_time is not None:
        return embargo_time
    return timezone.now()


def clear_embargo_time() -> None:
    """Clear the embargo_time for the current request context."""
    _embargo_time_ctx.set(None)
