import numpy as np
import pytest

from metrics.domain.charts import waffle


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
        logical_matrix: np.ndarray = waffle.build_two_dimensional_matrix(
            threshold=threshold, identifier=identifier
        )

        # Then
        expected_array = [identifier] * threshold
        expected_array += [0] * (100 - threshold)
        compared_two_dimensional_matrix: np.ndarray = (
            logical_matrix.flatten() == expected_array
        )
        assert compared_two_dimensional_matrix.all()

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
        matrix: np.ndarray = waffle.build_two_dimensional_matrix(
            threshold=threshold, identifier=1, length=length, width=width
        )

        # Then
        assert matrix.size == length * width

    def test_sum_is_equal_to_the_provided_threshold(self):
        """
        Given a certain `threshold`
        When `build_logical_matrix()` is called
        Then the `sum()` of the returned matrix is equal to the `threshold`
        """
        # Given
        threshold = 40

        # When
        matrix: np.ndarray = waffle.build_two_dimensional_matrix(
            threshold=threshold, identifier=1
        )

        # Then
        assert matrix.sum() == threshold

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
        matrix: np.ndarray = waffle.build_two_dimensional_matrix(
            threshold=threshold, identifier=identifier, length=length, width=width
        )

        # Then
        flattened_matrix: np.ndarray = matrix.flatten()
        assert flattened_matrix[0] == identifier

        for nan_value in flattened_matrix[threshold:]:
            np.isnan(nan_value)


class TestGetRgbColour:
    @pytest.mark.parametrize(
        "input_color, expected_string",
        [
            ("light_grey", "rgba(216,216,216,1)"),
            ("light_green", "rgba(119,196,191,1)"),
            ("middle_green", "rgba(0,156,145,1)"),
            ("dark_green", "rgba(0,65,61,1)"),
        ],
    )
    def test_returns_correct_string(self, input_color: str, expected_string: str):
        """
        Given a human-readable colour like "dark_green"
        When `get_rgb_colour()` is called
        Then the corresponding rgba colour representation is returned
        """
        # Given
        human_readable_colour: str = input_color

        # When
        rgb_colour_representation: str = waffle.get_rgb_colour(
            colour=human_readable_colour
        )

        # Then
        assert rgb_colour_representation == expected_string

    def test_raises_error_for_unsupported_colour(self):
        """
        Given a human-readable colour which is unsupported
        When `get_rgb_colour()` is called
        Then a `KeyError` is raised
        """
        # Given
        unsupported_colour = "non_existent_colour"

        # When / Then
        with pytest.raises(KeyError):
            waffle.get_rgb_colour(colour=unsupported_colour)


class TestGenerateChartFigure:
    def test_throws_error_when_more_than_three_data_points_provided(self):
        """
        Given more than 3 data point
        When `generate_chart_figure()` is called
        Then a `TooManyDataPointsError` is raised
        """
        # Given
        too_many_data_points = [78, 41, 22, 6]

        # When / Then
        with pytest.raises(waffle.TooManyDataPointsError):
            waffle.generate_chart_figure(data_points=too_many_data_points)
