import logging
from datetime import datetime, timezone


class AuditFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return (
            datetime.fromtimestamp(record.created, tz=timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%S.") + f"{record.msecs:03.0f}Z"
        )
