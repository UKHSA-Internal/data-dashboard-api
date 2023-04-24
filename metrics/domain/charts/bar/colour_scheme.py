from enum import Enum
from typing import Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAColours(Enum):
    # Used for the first plot
    PLOT_1_BLUE: RGBA_VALUES = 86, 148, 202, 1

    # Used for the second plot
    PLOT_2_GREY: RGBA_VALUES = 177, 180, 182, 1

    # Used for the background
    WHITE: RGBA_VALUES = 0, 0, 0, 0

    # Used to draw the axis
    DARK_BLUE_GREY: RGBA_VALUES = 107, 114, 118, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"
