import datetime

from django.utils import timezone


def cast_date_to_uk_timezone(date_value: datetime.datetime) -> datetime.datetime:
    """Casts the inbound `date_value` to the London timezone

    Args:
        date_value: The inbound date
            datetime object

    Returns:
        A `datetime` object which has the timezone
        info set to the declared `TIMEZONE` as per
        the main django settings

    """
    if date_value is None:
        return date_value

    try:
        return timezone.make_aware(value=date_value)
    except ValueError:
        # This is already time zone aware
        return date_value
