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
    return 1 if "weekly" in metric_name else 7
