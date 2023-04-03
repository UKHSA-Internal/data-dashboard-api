from enum import Enum
from typing import Tuple

RGBA_VALUES = Tuple[int, int, int, int]


class RGBAColours(Enum):
    # Used for the line plot
    BLACK: RGBA_VALUES = 0, 0, 0, 1

    # Used for the main background colour
    LIGHT_GREY: RGBA_VALUES = 248, 248, 248, 1

    # Used for the shaded filled region underneath the line plot
    DARK_GREY: RGBA_VALUES = 243, 242, 241, 1

    @property
    def stringified(self) -> str:
        return f"rgba{self.value}"
