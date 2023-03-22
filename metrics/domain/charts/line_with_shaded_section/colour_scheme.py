from enum import Enum
from typing import Dict, Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAColours(Enum):
    # Used for the background plot
    WHITE: RGBA_VALUES = 0, 0, 0, 0

    # Used for the good trending section
    DARK_GREEN: RGBA_VALUES = 0, 90, 48, 1
    LIGHT_GREEN: RGBA_VALUES = 204, 226, 216, 1

    # Used for the bad trending section
    DARK_RED: RGBA_VALUES = 148, 37, 20, 1
    LIGHT_RED: RGBA_VALUES = 246, 215, 210, 1

    # Used for the neutral trending section
    DARK_GREY: RGBA_VALUES = 56, 63, 67, 1
    LIGHT_GREY: RGBA_VALUES = 235, 233, 231, 1

    # Used to draw the axis
    DARK_BLUE_GREY: RGBA_VALUES = 107, 114, 118, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"


COLOURS: Dict[str, Dict[str, RGBAColours]] = {
    "positive": {"line": RGBAColours.DARK_GREEN, "fill": RGBAColours.LIGHT_GREEN},
    "negative": {"line": RGBAColours.DARK_RED, "fill": RGBAColours.LIGHT_RED},
    "neutral": {"line": RGBAColours.DARK_GREY, "fill": RGBAColours.LIGHT_GREY},
}


def _get_line_and_fill_colours(
    metric_is_improving: bool,
) -> Tuple[RGBAColours, RGBAColours]:
    if metric_is_improving:
        return RGBAColours.DARK_GREEN, RGBAColours.LIGHT_GREEN
    return RGBAColours.DARK_RED, RGBAColours.LIGHT_RED
