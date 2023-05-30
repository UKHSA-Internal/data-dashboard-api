import pytest

from metrics.domain.charts import colour_scheme


class TestRGBAColours:
    @pytest.mark.parametrize("rgba_enum", colour_scheme.RGBAColours)
    def test_stringified_returns_correct_string(
        self, rgba_enum: colour_scheme.RGBAColours
    ):
        """
        Given any of the values of the `RGBAColours` enum
        When the `stringified` property is called
        Then the correct string is returned for that enum value.

        E.g. If RGBAColours.PLOT_1_BLUE.stringified is called,
            then "rgba(86, 148, 202, 1)" is returned
        """
        # Given
        rgba_colour_enum: colour_scheme.RGBAColours = rgba_enum

        # When
        stringified_rgba_value: str = rgba_colour_enum.stringified

        # Then
        assert stringified_rgba_value == f"rgba{rgba_colour_enum.value}"
