from typing import List


def _calculate_average(values: List[int]) -> int:
    return sum(values) / len(values)


def calculate_average_difference_of_subslice(values: List[int], values_to_slice_count: int):
    """Returns the average value of the last x numbers in the given `values`.
    Where `x` is denoted by `values_to_slice_count`

    Examples:
        >>> calculate_average_difference_of_subslice([1, 2, 2], 2)
        0

        Where 0 is the average of the last 2 items,
        But the average of the entire list would be 1.66

    Args:
        values: List of numbers representing the values
        values_to_slice_count: The number of items to slice off
            from the end of `values` and perform the analysis on.

    Returns:

    """
    rolling_period_values = values[-values_to_slice_count:]
    start_value = rolling_period_values[0]

    average_over_rolling_period = _calculate_average(values=rolling_period_values)

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
