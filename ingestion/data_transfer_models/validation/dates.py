import datetime

import pytz


def cast_date_to_uk_timezone(*, date_value: datetime.datetime) -> datetime.datetime:
    """Casts the inbound `date_value`

    Args:
        date_value: The inbound date
            datetime object

    Returns:
        A `datetime` object which has the timezone
        info set to UTC

    """
    if date_value is None:
        return date_value

    utc_tz = pytz.timezone("UTC")
    try:
        return utc_tz.localize(dt=date_value).astimezone(tz=pytz.UTC)
    except ValueError:
        # This is already time zone aware
        return date_value
