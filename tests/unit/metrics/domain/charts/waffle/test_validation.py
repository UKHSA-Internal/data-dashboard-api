from typing import List

import pytest

from metrics.domain.charts.waffle import generation, validation


class TestGenerateChartFigure:
    def test_throws_error_when_more_than_three_data_points_provided(self):
        """
        Given more than 3 numbers in the provided `data_points`
        When `generate_chart_figure()` is called
        Then a `TooManyDataPointsError` is raised
        """
        # Given
        too_many_data_points = [78, 41, 22, 6]

        # When / Then
        with pytest.raises(validation.TooManyDataPointsError):
            generation.generate_chart_figure(values=too_many_data_points)

    @pytest.mark.parametrize(
        "data_points",
        [
            [41, 78],
            [41, 78, 90],
            [41, 90, 78],
        ],
    )
    def test_throws_error_when_data_points_are_not_in_descending_order(
        self, data_points: List[int]
    ):
        """
        Given a list of data points which are not in descending order
        When `generate_chart_figure()` is called
        Then a `DataPointsNotInDescendingOrderError` is raised

        Notes:
            The data_points must be in descending order.
            Otherwise, the largest value would be drawn with a darker colour.
            Which would in turn obfuscate the other plots
        """
        # Given
        data_points_in_descending_order = data_points

        # When / Then
        with pytest.raises(validation.DataPointsNotInDescendingOrderError):
            generation.generate_chart_figure(values=data_points_in_descending_order)
