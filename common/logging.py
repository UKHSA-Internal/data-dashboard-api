import logging
import typing
from datetime import UTC, datetime


class AuditFormatter(logging.Formatter):
    @typing.override
    def formatTime(self, record, datefmt=None):
        return (
            datetime.fromtimestamp(record.created, tz=UTC).strftime(
                "%Y-%m-%dT%H:%M:%S."
            )
            + f"{record.msecs:03.0f}Z"
        )
