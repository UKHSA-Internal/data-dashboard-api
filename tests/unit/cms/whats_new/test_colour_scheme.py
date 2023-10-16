import pytest

from cms.whats_new.colour_scheme import BadgeColours


class TestBadgeColours:
    @pytest.mark.parametrize(
        "conformant_colour",
        [
            "BLUE",
            "GREEN",
            "GREY",
            "ORANGE",
            "PINK",
            "PURPLE",
            "RED",
            "TURQUOISE",
            "YELLOW",
        ],
    )
    def test_enum_holds_correct_gds_conforming_colours(self, conformant_colour: str):
        """
        Given the `BadgeColours`  enum
        When one of the GDS-conformant colours is picked
        Then the corresponding enum is returned
        """
        # Given
        badge_colours = BadgeColours

        # When
        badge_colour: BadgeColours = getattr(badge_colours, conformant_colour)

        # Then
        assert badge_colour.value == conformant_colour

    @pytest.mark.parametrize(
        "non_conformant_colour",
        [
            "LIGHT_BLUE",
            "BLACK",
            "WHITE",
        ],
    )
    def test_enum_raises_error_for_non_gds_conforming_colours(
        self, non_conformant_colour: str
    ):
        """
        Given the `BadgeColours`  enum
        When a colour which does not conform
            to the GDS specification for tags is picked
        Then an `AttributeError` is raised
        """
        # Given
        badge_colours = BadgeColours

        # When / Then
        with pytest.raises(AttributeError):
            getattr(badge_colours, "expected_colour")
