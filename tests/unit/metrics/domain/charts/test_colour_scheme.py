import pytest

from metrics.domain.charts.colour_scheme import RGBAChartLineColours


class TestRGBAChartLineColours:
    @pytest.mark.parametrize("rgba_enum", RGBAChartLineColours)
    def test_stringified_returns_correct_string(self, rgba_enum: RGBAChartLineColours):
        """
        Given any of the values of the `RGBAChartLineColours` enum
        When the `stringified` property is called
        Then the correct string is returned for that enum value.

        E.g. If RGBAChartLineColours.WHITE.stringified is called,
            then "rgba(0, 0, 0, 0)" is returned
        """
        # Given
        rgba_colour_enum: RGBAChartLineColours = rgba_enum

        # When
        stringified_rgba_value: str = rgba_colour_enum.stringified

        # Then
        assert stringified_rgba_value == f"rgba{rgba_colour_enum.value}"

    @pytest.mark.parametrize("rgba_enum", RGBAChartLineColours)
    def test_get_colour(self, rgba_enum: RGBAChartLineColours):
        """
        Given a valid colour string e.g. "RED"
        When `get_colour()` is called from the `RGBAColours` class
        Then the correct enum is returned
        """
        # Given
        colour: str = rgba_enum.name

        # When
        retrieved_colour: RGBAChartLineColours = RGBAChartLineColours.get_colour(
            colour=colour
        )

        # Then
        assert type(retrieved_colour) is RGBAChartLineColours
        assert retrieved_colour.name == colour

    @pytest.mark.parametrize(
        "invalid_colour", [(None, "null", "", "NON-EXISTENT-COLOUR", "CORAL")]
    )
    def test_get_colour_defaults_to_black(self, invalid_colour: str | None):
        """
        Given an invalid colour which is not available as a GDS-conforming colour
        When `get_colour()` is called from the `RGBAColours` class
        Then the `BLACK` enum is defaulted to and returned
        """
        # Given
        colour: str = invalid_colour

        # When
        retrieved_colour = RGBAChartLineColours.get_colour(colour=colour)

        # Then
        assert type(retrieved_colour) is RGBAChartLineColours
        assert retrieved_colour == RGBAChartLineColours.BLACK
