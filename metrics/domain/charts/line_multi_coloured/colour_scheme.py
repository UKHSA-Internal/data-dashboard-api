from enum import Enum
from typing import Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAColours(Enum):
    # Used for the background plot
    WHITE: RGBA_VALUES = 0, 0, 0, 0

    RED: RGBA_VALUES = 212, 53, 28, 1
    YELLOW: RGBA_VALUES = 255, 221, 0, 1
    GREEN: RGBA_VALUES = 0, 112, 60, 1
    BLUE: RGBA_VALUES = 29, 112, 184, 1
    DARK_BLUE: RGBA_VALUES = 0, 48, 120, 1
    LIGHT_BLUE: RGBA_VALUES = 86, 148, 202, 1
    PURPLE: RGBA_VALUES = 76, 44, 146, 1
    BLACK: RGBA_VALUES = 11, 12, 12, 1
    DARK_GREY: RGBA_VALUES = 80, 90, 95, 1
    MID_GREY: RGBA_VALUES = 177, 180, 182, 1
    LIGHT_GREY: RGBA_VALUES = 243, 242, 241, 1
    LIGHT_PURPLE: RGBA_VALUES = 111, 114, 175, 1
    BRIGHT_PURPLE: RGBA_VALUES = 145, 43, 136, 1
    PINK: RGBA_VALUES = 213, 56, 128, 1
    LIGHT_PINK: RGBA_VALUES = 244, 153, 190, 1
    ORANGE: RGBA_VALUES = 244, 119, 56, 1
    BROWN: RGBA_VALUES = 181, 136, 64, 1
    LIGHT_GREEN: RGBA_VALUES = 133, 153, 75, 1
    TURQUOISE: RGBA_VALUES = 40, 161, 151, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"

    @classmethod
    def choices(cls):
        return tuple((chart_type.name, chart_type.name) for chart_type in cls)

    @classmethod
    def get_colour(cls, colour: str) -> "RGBAColours":
        try:
            return cls[colour]
        except KeyError:
            return cls.BLACK
