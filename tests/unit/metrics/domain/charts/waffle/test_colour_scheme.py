import pytest

from metrics.domain.charts.waffle import colour_scheme


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
        rgb_colour_representation: str = colour_scheme.get_rgb_colour(
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
            colour_scheme.get_rgb_colour(colour=unsupported_colour)
