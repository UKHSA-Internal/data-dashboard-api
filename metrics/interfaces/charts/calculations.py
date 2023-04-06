from typing import Tuple, Union


def change_between_each_half(values: list) -> Union[int, float]:
    """Calculates the difference between the total of each half of the `values`

    Args:
        values: List of numbers

    Returns:
        A number representing the difference of
        the sum of each half of the list.

    """
    first_half_values, second_half_values = split_list_in_half(values=values)
    return sum(second_half_values) - sum(first_half_values)


def split_list_in_half(values: list) -> Tuple[list, list]:
    half = len(values) // 2
    return values[:half], values[half:]


def get_rolling_period_slice_for_metric(metric_name: str) -> int:
    """Gets the number of points needed to be sliced for the rolling period of the given `metric`

    Args:
        metric_name: The name of the metric being checked.
            E.g. `new_cases_daily`

    Returns:
        The number of points which would represent
        the rolling period of that metric.

    """
    return 1 if "weekly" in metric_name else 7
