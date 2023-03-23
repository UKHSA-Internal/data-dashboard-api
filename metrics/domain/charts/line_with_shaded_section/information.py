from typing import List, Tuple

from metrics.domain.charts import type_hints
from metrics.domain.charts.line_with_shaded_section import colour_scheme


def determine_line_and_fill_colours(
    values: List[int], last_n_values_to_analyse: int, metric_name: str
) -> type_hints.COLOUR_PAIR:
    """Returns colours dependening on whether the average change in `last_n_values_to_analyse` is considered to begood.

    For example, for cases or deaths, an average increase in the `last_n_values_to_analyse`
    would be considered to be negative. Which would return a pair of red colours.
    But, for vaccinations an increase in the corresponding average change
    would be considered to be positive. Which would return a pair of green colours.

    Examples:
        >>> determine_line_and_fill_colours([5, 3, 2], 2, metric_name='new_cases_daily')
        (colour_scheme.RGBAColours.DARK_GREEN, colour_scheme.RGBAColours.LIGHT_GREEN)

        >>> is_metric_improving([1, 3, 7], 2, metric_name='new_cases_daily')
        (colour_scheme.RGBAColours.DARK_RED, colour_scheme.RGBAColours.LIGHT_RED)

    Args:
        values: List of numbers representing the values
        last_n_values_to_analyse: The number of items to slice off
            from the end of `values` and perform the analysis on.
        metric_name: The associated metric_name,
            E.g. new_admissions_daily

    Returns:
        Tuple[colour_scheme.RGBAColours, colour_scheme.RGBAColours]:
            A pair of colours depending on whether
            the analysed slice is considered to be
            a good thing or a bad thing.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    change_in_metric_value = calculate_average_difference_of_subslice(
        values=values, last_n_values_to_analyse=last_n_values_to_analyse
    )

    metric_is_improving = is_metric_improving(
        change_in_metric_value=change_in_metric_value,
        metric_name=metric_name,
    )

    return colour_scheme._get_line_and_fill_colours(
        metric_is_improving=metric_is_improving
    )


def _calculate_mean(values: List[int]) -> float:
    return sum(values) / len(values)


def calculate_average_difference_of_subslice(
    values: List[int], last_n_values_to_analyse: int
):
    """Returns the average value of the `last_n_values_to_analyse` in the given `values`.

    Examples:
        >>> calculate_average_difference_of_subslice([1, 2, 2], 2)
        0

        Where 0 is the average of the last 2 items,
        But the average of the entire list would be 1.66

    Args:
        values: List of numbers representing the values
        last_n_values_to_analyse: The number of items to slice off
            from the end of `values` and perform the analysis on.

    Returns:

    """
    rolling_period_values = values[-last_n_values_to_analyse:]
    start_value = rolling_period_values[0]

    average_over_rolling_period: float = _calculate_mean(values=rolling_period_values)

    return round(average_over_rolling_period - start_value, 2)


def is_metric_improving(change_in_metric_value: int, metric_name: str) -> bool:
    """Checks whether a positive or negative `change_in_metric_value` should be considered a good thing.

    For example, for cases or deaths, an increase in metric value
    would be considered to be negative.
    But, for vaccinations an increase in the corresponding metric value
    would be considered to be positive.

    Examples:
        >>> is_metric_improving(change_in_metric_value=20, metric_name='new_cases_daily')
        False

        >>> is_metric_improving(change_in_metric_value=-20, metric_name='new_cases_daily')
        True

    Args:
        `change_in_metric_value`: The change in metric value,
            as a number. E.g. -10
        `metric_name`: The associated metric_name,
            E.g. new_admissions_daily

    Returns:
        bool: True if the change in value is to be considered
            positive relative to that metric. False otherwise.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    increasing_is_bad = (
        "cases",
        "deaths",
        "admissions",
        "covid_occupied",
        "positivity",
    )
    increasing_is_good = ("vaccines", "vaccination", "vaccinated", "tests", "pcr")

    if _check_for_substring_match(
        string_to_check=metric_name, substrings=increasing_is_bad
    ):
        return change_in_metric_value < 0

    if _check_for_substring_match(
        string_to_check=metric_name, substrings=increasing_is_good
    ):
        return change_in_metric_value > 0

    raise ValueError(f"{metric_name} is not supported")


def _check_for_substring_match(string_to_check: str, substrings: List[str]) -> bool:
    return any((sub_string in string_to_check for sub_string in substrings))
