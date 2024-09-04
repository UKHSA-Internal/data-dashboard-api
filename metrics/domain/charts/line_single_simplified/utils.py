from decimal import Decimal

SUFFIXES = ["", "k", "m"]
E_NOTATION = [1e0, 1e3, 1e6, 1e9]
CONVERT_LARGE_NUMBERS_VALUE_ERROR = (
    "This number is to large to be formatted for the simplified chart."
)


def convert_large_numbers_to_short_text(number: int) -> str:
    """Converts the provided `int` into a short number string.

    Args:
        number: Integer to be formatted as a string

    Returns:
        A short number string
        Eg: 1000 = 1k, 2500 = 2k, 2690 = 3k, 100,000,000 = 1m
    """
    if number >= E_NOTATION[1]:

        for index in range(len(E_NOTATION)):
            try:
                if E_NOTATION[index] <= number < E_NOTATION[index + 1]:
                    return f"{str(int(number / E_NOTATION[index]))}{SUFFIXES[index]}"

            except IndexError:
                raise ValueError(CONVERT_LARGE_NUMBERS_VALUE_ERROR)

    return str(number)


def _extract_max_value(
    y_axis_values: list[Decimal],
) -> int:
    """Extracts the highest `Decimal` value from the `y_axis_values`
        list and returns an `Int` rounded to the nearest large number

    Notes:
        `place_value` is the place of the first digit in the number
        represented by the number of digits to its right.
        Eg: a number of `1000` has 3 places after the first digit
        so `place_value` = 3

    Args:
        y_axis_values: list of Decimal values

    Returns:
        an integer of the highest value from the list rounded to the
        nearest 10, 100, 1000, ... depending on the number provided.
    """
    max_y_axis_value = round(max(y_axis_values))
    place_value = len(str(max_y_axis_value)) - 1
    return round(max_y_axis_value, -place_value)


def return_formatted_max_y_axis_value(
    y_axis_values: list[Decimal],
) -> str:
    """Returns the highest value from `y_axis_values` as a formatted string

    Args:
        y_axis_values: A list of `Decimal` values representing
        the y_axis values of a `Timeseries` chart.

    Returns:
        A string of the highest value from `y_axis_values` rounded up
        and formatted as a short string Eg: 1400 becomes 1k
    """
    max_value = _extract_max_value(y_axis_values=y_axis_values)
    return convert_large_numbers_to_short_text(number=max_value)
