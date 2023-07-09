import pytest

from metrics.domain.charts.waffle import generation, validation


class TestGenerateChartFigure:
    def test_throws_error_when_more_than_three_values_provided(self):
        """
        Given more than 3 numbers in the provided `values`
        When `generate_chart_figure()` is called
        Then a `TooManyDataPointsError` is raised
        """
        # Given
        too_many_values = [78, 41, 22, 6]

        # When / Then
        with pytest.raises(validation.TooManyDataPointsError):
            generation.generate_chart_figure(values=too_many_values)

    @pytest.mark.parametrize(
        "values",
        [
            [41, 78],
            [41, 78, 90],
            [41, 90, 78],
        ],
    )
    def test_throws_error_when_values_are_not_in_descending_order(
        self, values: list[int]
    ):
        """
        Given a list of `values` which are not in descending order
        When `generate_chart_figure()` is called
        Then a `DataPointsNotInDescendingOrderError` is raised

        Notes:
            The values must be in descending order.
            Otherwise, the largest value would be drawn with a darker colour.
            Which would in turn obfuscate the other plots
        """
        # Given
        values_in_descending_order = values

        # When / Then
        with pytest.raises(validation.DataPointsNotInDescendingOrderError):
            generation.generate_chart_figure(values=values_in_descending_order)
