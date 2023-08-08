import numpy as np

from metrics.domain.charts.waffle import pre_processing


class TestBuildTwoDimensionalMatrix:
    def test_output_array_contains_expected_values(self):
        """
        Given a certain `threshold`
        When `build_logical_matrix()` is called
        Then a 2D array is returned with the correct values
        """
        # Given
        threshold = 30
        identifier = 1

        # When
        logical_matrix: list[
            list[int | str]
        ] = pre_processing.build_two_dimensional_matrix(
            threshold=threshold, identifier=identifier
        )

        # Then
        expected_array = [identifier] * threshold
        expected_array += [0] * (100 - threshold)
        logical_matrix_flattened: list[int | str] = [
            item for sub_list in logical_matrix for item in sub_list
        ]
        assert logical_matrix_flattened == expected_array

    def test_matrix_size_is_determined_by_the_input_dimensions(self):
        """
        Given custom dimensions for the `length` and `width`
        When `build_logical_matrix()` is called
        Then the `size()` of the returned matrix
            is equal to the multiplied value of `length` and `width`
        """
        # Given
        threshold = 40
        length = 2
        width = 2

        # When
        matrix: list[list[int | str]] = pre_processing.build_two_dimensional_matrix(
            threshold=threshold, identifier=1, length=length, width=width
        )
        matrix_size = len([value for sub_list in matrix for value in sub_list])

        # Then
        assert matrix_size == length * width

    def test_sum_is_equal_to_the_provided_threshold(self):
        """
        Given a certain `threshold`
        When `build_logical_matrix()` is called
        Then the `sum()` of the returned matrix is equal to the `threshold`
        """
        # Given
        threshold = 40

        # When
        matrix: np.ndarray = pre_processing.build_two_dimensional_matrix(
            threshold=threshold, identifier=1
        )
        matrix_sum = sum([value for sub_list in matrix for value in sub_list])

        # Then
        assert matrix_sum == threshold

    def test_nan_values_are_used_for_zero_values_for_larger_identifiers(self):
        """
        Given an identifier which is greater than 1
        And custom dimensions for the `length` and `width`
        When `build_logical_matrix()` is called
        Then `0` values are replaced with `NaN` values
        """
        # Given
        threshold = 1
        length = 2
        width = 2
        identifier = 2

        # When
        matrix: np.ndarray = pre_processing.build_two_dimensional_matrix(
            threshold=threshold, identifier=identifier, length=length, width=width
        )

        # Then
        flattened_matrix: list[int | stre] = [
            value for sub_list in matrix for value in sub_list
        ]
        assert flattened_matrix[0] == identifier

        for nan_value in flattened_matrix[threshold:]:
            assert nan_value == "NaN"
