import datetime

PERIOD_END_NOT_GIVEN_ERROR_MESSAGE = "The 'period_start' was given as null"
PERIOD_DATES_INVALID_MESSAGE = (
    "The `period_start` and `period_end` were not given in chronological order"
)


def validate_period_end(
    *, period_start: datetime.datetime, period_end: datetime.datetime
) -> datetime.date:
    """Validates the `period_start` and `period_end` fields to check they conform to the expected rules

    Notes:
        The `period_end` must be after the `period_start`,
        otherwise these validation checks will fail.
        If they are the same date then this is valid.

    Args:
        period_start: The start date for the period
            encapsulated by this headline metric data
        period_end: The end date for the period
            encapsulated by this headline metric data

    Returns:
        The input `period_end` unchanged if
        it has passed the validation checks.

    Raises:
        `ValueError`: If any of the validation checks fail

    """
    if period_start is None:
        raise ValueError(PERIOD_END_NOT_GIVEN_ERROR_MESSAGE)

    return _validate_period_dates_in_correct_order(
        period_start=period_start, period_end=period_end
    )


def _validate_period_dates_in_correct_order(
    *,
    period_start: datetime.date,
    period_end: datetime.date,
) -> datetime.date:
    if period_end >= period_start:
        return period_end
    raise ValueError(PERIOD_DATES_INVALID_MESSAGE)
