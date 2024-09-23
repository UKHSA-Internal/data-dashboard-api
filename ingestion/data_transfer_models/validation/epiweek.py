import datetime

import epiweeks


def validate_epiweek(*, input_epiweek: int, input_date: datetime.date) -> int:
    """Checks to see if the given `input_epiweek` is valid for the `input_date`

    Args:
        `input_epiweek`: The epiweek number
        `input_date`: The associated date of the record

    Returns:
        The validated epiweek number

    Raises:
        `ValueError`: If the given date was not calculated
            as being within the given epiweek

    """
    week = epiweeks.Week.fromdate(date_object=input_date, system="iso")
    if week.week == input_epiweek:
        return input_epiweek

    error_message = f"Input epiweek of `{input_epiweek}` is not valid to calculated no. of `{week.week}`"
    raise ValueError(error_message)
