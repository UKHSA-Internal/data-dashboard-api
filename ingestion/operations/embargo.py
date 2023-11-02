import datetime


def _get_current_datetime() -> datetime.datetime:
    return datetime.datetime.now()


def _get_next_thursday_cutoff_time(
    current_datetime: datetime.datetime,
) -> datetime.datetime:
    number_days_until_next_thursday: int = (3 - current_datetime.weekday()) % 7

    next_thursday: datetime.datetime = current_datetime + datetime.timedelta(
        days=number_days_until_next_thursday
    )
    return next_thursday.replace(hour=17, minute=30, second=0)


def get_default_embargo() -> datetime.datetime:
    """Gets a default embargo of the next available Thursday 5.30pm

    Notes:
        This enforces a hard cutoff of Thursday 5.30pm.

        - If the current datetime is between Thursday 12.00am - 5.29 pm
        then the embargo will be set for 5.30pm
        i.e. for that same day

        - If the current datetime is past Thursday 5.31 pm
        then the embargo will be set for the following Thursday 5.30pm
        i.e. 1 week later

        - If the current datetime is anytime between Friday - Wednesday
        then the embargo will be set for the next possible Thursday
        i.e. less than 6 days later
        For example, if the current datetime is Monday 11am,
        then the returned datetime will be the Thursday 5.30pm
        of that same week.

    Returns:
        A `datetime` object for the next valid Thursday 5.30pm

    """
    current_datetime = _get_current_datetime()
    next_thursday_cutoff_time: datetime.datetime = _get_next_thursday_cutoff_time(
        current_datetime=current_datetime
    )

    if current_datetime >= next_thursday_cutoff_time:
        next_thursday_cutoff_time += datetime.timedelta(7)

    return next_thursday_cutoff_time
