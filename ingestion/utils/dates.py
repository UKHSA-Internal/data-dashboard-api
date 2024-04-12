import datetime


def calculate_days_between_dates(dates: list[datetime.date]) -> set[int]:
    """Calculates the possible/unique days between each date

    Args:
        dates: The list of dates in chronological order

    Returns:
        A set containing the unique numbers of
        calculated days between each date.

    """
    days_between = set()
    for i in range(len(dates) - 1):
        day_ahead: datetime.date = dates[i + 1]
        current_day: datetime.date = dates[i]

        difference: datetime.timedelta = day_ahead - current_day
        calculated_days_between: int = difference.days

        days_between.add(calculated_days_between)

    return days_between
