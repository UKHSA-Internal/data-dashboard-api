from enum import Enum
from typing import Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAChartLineColours(Enum):
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
    def get_colour(cls, colour: str) -> "RGBAPlotColours":
        try:
            return cls[colour]
        except KeyError:
            return cls.BLACK


class RGBAColours(Enum):
    # Used for the line plot
    BLACK: RGBA_VALUES = 0, 0, 0, 1

    # Used for the background
    WHITE: RGBA_VALUES = 0, 0, 0, 0

    # Used to draw the tick labels
    DARK_BLUE_GREY: RGBA_VALUES = 107, 114, 118, 1

    # Used for the background plot colour
    LIGHT_GREY: RGBA_VALUES = 231, 231, 231, 0

    # Used for the neutral cells which do not have a threshold value
    GREY: RGBA_VALUES = 216, 216, 216, 1

    # --------------------
    # Line chart specific
    # --------------------

    # Used for the main background colour (in Line charts)
    LINE_LIGHT_GREY: RGBA_VALUES = 248, 248, 248, 1

    # Used for the shaded filled region underneath the line plot (in Line charts)
    LINE_DARK_GREY: RGBA_VALUES = 243, 242, 241, 1

    # -------------------
    # Bar chart specific
    # -------------------

    # Used for the first plot
    BAR_PLOT_1_BLUE: RGBA_VALUES = 86, 148, 202, 1

    # ----------------------
    # Waffle chart specific
    # ----------------------

    # Used for the background paper colour
    WAFFLE_WHITE: RGBA_VALUES = 255, 255, 255, 0

    # Used for the 1st value
    LIGHT_GREEN: RGBA_VALUES = 119, 196, 191, 1

    # Used for the 2nd value
    MIDDLE_GREEN: RGBA_VALUES = 0, 156, 145, 1

    # Used for the 3rd value
    DARK_GREEN: RGBA_VALUES = 0, 65, 65, 1

    # ----------------------------------------
    # Line with shaded section chart specific
    # ----------------------------------------

    # Used for the good trending section
    LS_DARK_GREEN: RGBA_VALUES = 0, 90, 48, 1
    LS_LIGHT_GREEN: RGBA_VALUES = 204, 226, 216, 1

    # Used for the bad trending section
    DARK_RED: RGBA_VALUES = 148, 37, 20, 1
    LIGHT_RED: RGBA_VALUES = 246, 215, 210, 1

    # Used for the neutral trending section
    LS_DARK_GREY: RGBA_VALUES = 56, 63, 67, 1
    LS_LIGHT_GREY: RGBA_VALUES = 235, 233, 231, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"
