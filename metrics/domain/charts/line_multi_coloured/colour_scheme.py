from enum import Enum
from typing import Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAColours(Enum):
    # Used for the background plot
    WHITE: RGBA_VALUES = 0, 0, 0, 0

    # Used to draw the axis
    DARK_BLUE_GREY: RGBA_VALUES = 107, 114, 118, 1

    # The colours made available to the individual line plots
    PLOT_DARK_GREEN: RGBA_VALUES = 0, 90, 48, 1
    PLOT_DARK_RED: RGBA_VALUES = 148, 37, 20, 1
    PLOT_DARK_GREY: RGBA_VALUES = 56, 63, 67, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"

    @classmethod
    def available_plot_colours(cls):
        return [cls for cls in cls if cls.name.startswith("PLOT")]
