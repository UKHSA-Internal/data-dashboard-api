from enum import Enum
from typing import List, Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAColours(Enum):
    # Used for the background paper colour
    WHITE: RGBA_VALUES = 255, 255, 255, 0

    # Used for the background plot colour
    LIGHT_GREY: RGBA_VALUES = 231, 231, 231, 0

    # Used for the neutral cells which do not have a threshold value
    GREY: RGBA_VALUES = 216, 216, 216, 1

    # Used for the 1st value
    LIGHT_GREEN: RGBA_VALUES = 119, 196, 191, 1

    # Used for the 2nd value
    MIDDLE_GREEN: RGBA_VALUES = 0, 156, 145, 1

    # Used for the 3rd value
    DARK_GREEN: RGBA_VALUES = 0, 65, 65, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"


class InvalidIdentifierError(Exception):
    ...


def build_color_scale(identifier: int) -> List[List]:
    """Builds the colour scale for the waffle chart plot based on the identifier.

    Args:
        identifier: The position of the plot.
            Currently, this can only be 1, 2 or 3.

    Returns:
        List[list[int, str]]: A nested list of values.
            >>> [
                    [0, 'rgba(216,216,216,1)'],
                    [0.5, 'rgba(0,156,145,1)'],
                    [0.9, 'rgba(0,156,145,1)'],
                    [1, 'rgba(0,156,145,1)'],
            ]

    Raises:
        `InvalidIdentifierError`: If an identifier which is not
            either 1, 2 or 3 is provided.

    """
    background_rgb_colour: str = RGBAColours.GREY.stringified

    if identifier == 3:
        darkest_plot_rgb_colour: str = RGBAColours.DARK_GREEN.stringified
        return [
            [0, background_rgb_colour],
            [0.5, darkest_plot_rgb_colour],
            [0.9, darkest_plot_rgb_colour],
            [1, darkest_plot_rgb_colour],
        ]

    if identifier == 2:
        middle_plot_rgb_colour: str = RGBAColours.MIDDLE_GREEN.stringified
        return [
            [0, background_rgb_colour],
            [0.5, middle_plot_rgb_colour],
            [0.9, middle_plot_rgb_colour],
            [1, middle_plot_rgb_colour],
        ]
    if identifier == 1:
        lightest_plot_rgb_colour: str = RGBAColours.LIGHT_GREEN.stringified
        return [
            [0, background_rgb_colour],
            [0.5, background_rgb_colour],
            [0.9, lightest_plot_rgb_colour],
            [1, lightest_plot_rgb_colour],
        ]

    raise InvalidIdentifierError()
