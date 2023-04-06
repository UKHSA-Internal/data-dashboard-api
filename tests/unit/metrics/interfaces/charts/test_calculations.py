from typing import List

import pytest

from metrics.interfaces.charts import calculations


@pytest.mark.parametrize(
    "original_list, expected_first_half, expected_second_half",
    (
        ([1, 2], [1], [2]),
        ([1, 2, 3], [1], [2, 3]),
        ([1, 2, 3, 4], [1, 2], [3, 4]),
    ),
)
def test_split_list_in_half(
    original_list: List[int],
    expected_first_half: List[int],
    expected_second_half: List[int],
):
    """
    Given a list of integers
    When `split_list_in_half()` is called
    Then the list is split into 2 halves
    """
    # Given
    values = original_list

    # When
    first_half, second_half = calculations.split_list_in_half(values=values)

    # Then
    assert first_half == expected_first_half
    assert second_half == expected_second_half


def test_split_list_in_half_for_fourteen_length_list():
    """
    Given a list of 14 numbers
    When `split_list_in_half()` is called
    Then the list is split into 2 halves
    """
    # Given
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    # When
    first_half, second_half = calculations.split_list_in_half(values=values)

    # Then
    assert first_half == [1, 2, 3, 4, 5, 6, 7]
    assert second_half == [8, 9, 10, 11, 12, 13, 14]


def test_change_over_each_half():
    """
    Given a list of values
    When `change_over_each_half()` is called
    Then the correct calculated change in value between each half is returned
    """
    # Given
    values = [1, 2, 3, 5]

    # When
    calculated_change = calculations.change_over_each_half(values=values)

    # Then
    assert calculated_change == 1
