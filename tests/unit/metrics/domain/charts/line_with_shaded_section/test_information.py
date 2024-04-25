from metrics.domain.charts import colour_scheme
from metrics.domain.charts.line_with_shaded_section.information import (
    determine_line_and_fill_colours,
)


class TestDetermineLineAndFillColours:
    def test_returns_green_colours_for_decreasing_cases(self):
        """
        Given a `change_in_metric_value` which is decreasing
        And a `metric_name` of "new_cases_daily"
        When `determine_line_and_fill_colours()` is called
        Then a pair of green colours is returned
        """
        # Given
        change_in_metric_value = -10
        metric_name = "new_cases_daily"

        # When
        line_colour, fill_colour = determine_line_and_fill_colours(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric_name,
        )

        # Then
        assert line_colour == colour_scheme.RGBAColours.LS_DARK_GREEN
        assert fill_colour == colour_scheme.RGBAColours.LS_LIGHT_GREEN

    def test_returns_red_colours_for_increasing_cases(self):
        """
        Given a `change_in_metric_value` which is increasing
        And a `metric_name` of "new_cases_daily"
        When `determine_line_and_fill_colours()` is called
        Then a pair of red colours is returned
        """
        # Given
        change_in_metric_value = 10
        metric_name = "new_cases_daily"

        # When
        line_colour, fill_colour = determine_line_and_fill_colours(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric_name,
        )

        # Then
        assert line_colour == colour_scheme.RGBAColours.DARK_RED
        assert fill_colour == colour_scheme.RGBAColours.LIGHT_RED
