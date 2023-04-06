from typing import Tuple, Union


def change_over_each_half(values: list) -> Union[int, float]:
    first_half_values, second_half_values = split_list_in_half(values=values)

    change_in_first_half_values = first_half_values[-1] - first_half_values[0]
    change_in_second_half_values = second_half_values[-1] - second_half_values[0]

    return change_in_second_half_values - change_in_first_half_values


def split_list_in_half(values: list) -> Tuple[list, list]:
    half = len(values) // 2
    return values[:half], values[half:]
