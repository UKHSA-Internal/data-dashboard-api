from metrics.domain.charts import colour_scheme
from metrics.domain.charts.waffle.colour_scheme import build_color_scale


class TestBuildColorScale:
    def test_identifier_three_produces_darkest_scale(self):
        """
        Given an identifier of 3
        When `build_color_scale()` is called
        Then a list of nested lists referencing a dark colour scale is returned
        """
        # Given
        identifier = 3

        # When
        colour_scale: list[list[int, str]] = build_color_scale(identifier=identifier)

        # Then
        expected_colour_scale = [
            [0, colour_scheme.RGBAColours.GREY.stringified],
            [0.5, colour_scheme.RGBAColours.DARK_GREEN.stringified],
            [0.9, colour_scheme.RGBAColours.DARK_GREEN.stringified],
            [1, colour_scheme.RGBAColours.DARK_GREEN.stringified],
        ]
        assert colour_scale == expected_colour_scale

    def test_identifier_two_produces_middle_scale(self):
        """
        Given an identifier of 2
        When `build_color_scale()` is called
        Then a list of nested lists referencing a middle colour scale is returned
        """
        # Given
        identifier = 2

        # When
        colour_scale: list[list[int, str]] = build_color_scale(identifier=identifier)

        # Then
        expected_colour_scale = [
            [0, colour_scheme.RGBAColours.GREY.stringified],
            [0.5, colour_scheme.RGBAColours.MIDDLE_GREEN.stringified],
            [0.9, colour_scheme.RGBAColours.MIDDLE_GREEN.stringified],
            [1, colour_scheme.RGBAColours.MIDDLE_GREEN.stringified],
        ]
        assert colour_scale == expected_colour_scale

    def test_identifier_one_produces_lightest_scale(self):
        """
        Given an identifier of 2
        When `build_color_scale()` is called
        Then a list of nested lists referencing a light colour scale is returned
        """
        # Given
        identifier = 1

        # When
        colour_scale: list[list[int, str]] = build_color_scale(identifier=identifier)

        # Then
        expected_colour_scale = [
            [0, colour_scheme.RGBAColours.GREY.stringified],
            [0.5, colour_scheme.RGBAColours.GREY.stringified],
            [0.9, colour_scheme.RGBAColours.LIGHT_GREEN.stringified],
            [1, colour_scheme.RGBAColours.LIGHT_GREEN.stringified],
        ]
        assert colour_scale == expected_colour_scale
