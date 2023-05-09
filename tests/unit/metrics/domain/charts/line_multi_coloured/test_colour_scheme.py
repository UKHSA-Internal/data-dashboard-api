from typing import List

import pytest

from metrics.domain.charts.line_multi_coloured import colour_scheme


class TestRGBAColours:
    @pytest.mark.parametrize("rgba_enum", colour_scheme.RGBAColours)
    def test_stringified_returns_correct_string(
        self, rgba_enum: colour_scheme.RGBAColours
    ):
        """
        Given any of the values of the `RGBAColours` enum
        When the `stringified` property is called
        Then the correct string is returned for that enum value.

        E.g. If RGBAColours.WHITE.stringified is called,
            then "rgba(0, 0, 0, 0)" is returned
        """
        # Given
        rgba_colour_enum: colour_scheme.RGBAColours = rgba_enum

        # When
        stringified_rgba_value: str = rgba_colour_enum.stringified

        # Then
        assert stringified_rgba_value == f"rgba{rgba_colour_enum.value}"

    def test_available_plot_colours_returns_correct_enums(self):
        """
        Given the `RGBAColours` enum class
        When `available_plot_colours()` is called from the class
        Then a list of enums is returned which all start with "PLOT"
        """
        # Given / When
        plot_colour_enums: List[
            colour_scheme.RGBAColours
        ] = colour_scheme.RGBAColours.available_plot_colours()

        # When
        assert all(enum.name.startswith("PLOT") for enum in plot_colour_enums)
