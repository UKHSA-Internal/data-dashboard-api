from enum import Enum

RGBA_VALUES = tuple[int, int, int]


class RGBAChartLineColours(Enum):
    COLOUR_1_DARK_BLUE = 18, 67, 109
    COLOUR_2_TURQUOISE = 40, 161, 151
    COLOUR_3_DARK_PINK = 128, 22, 80
    COLOUR_4_ORANGE = 244, 106, 37
    COLOUR_5_DARK_GREY = 61, 61, 61
    COLOUR_6_LIGHT_PURPLE = 162, 133, 209
    COLOUR_7_BURGUNDY = 84, 13, 52
    COLOUR_8_MUSTARD = 194, 132, 0
    COLOUR_9_DEEP_PLUM = 51, 25, 77
    COLOUR_10_PINK = 229, 102, 183
    COLOUR_11_KHAKI = 71, 71, 0
    COLOUR_12_BLUE = 0, 157, 214

    MAP_COLOUR_1_LIGHT_YELLOW = 240, 249, 232
    MAP_COLOUR_2_LIGHT_GREEN = 186, 228, 188
    MAP_COLOUR_3_TURQUOISE = 123, 204, 196
    MAP_COLOUR_4_BLUE = 67, 162, 202
    MAP_COLOUR_5_DARK_BLUE = 8, 104, 172

    # simplified single line chart colours
    TREND_LINE_POSITIVE = 0, 112, 60
    TREND_LINE_NEGATIVE = 171, 43, 23
    TREND_LINE_NEUTRAL = 56, 63, 67

    # Legacy colors
    RED: RGBA_VALUES = 212, 53, 28
    YELLOW: RGBA_VALUES = 255, 221, 0
    GREEN: RGBA_VALUES = 0, 112, 60
    BLUE: RGBA_VALUES = 29, 112, 184
    DARK_BLUE: RGBA_VALUES = 0, 48, 120
    LIGHT_BLUE: RGBA_VALUES = 86, 148, 202
    PURPLE: RGBA_VALUES = 76, 44, 146
    BLACK: RGBA_VALUES = 11, 12, 12
    DARK_GREY: RGBA_VALUES = 80, 90, 95
    MID_GREY: RGBA_VALUES = 177, 180, 182
    LIGHT_GREY: RGBA_VALUES = 243, 242, 241
    LIGHT_PURPLE: RGBA_VALUES = 111, 114, 175
    BRIGHT_PURPLE: RGBA_VALUES = 145, 43, 136
    PINK: RGBA_VALUES = 213, 56, 128
    LIGHT_PINK: RGBA_VALUES = 244, 153, 190
    ORANGE: RGBA_VALUES = 244, 119, 56
    BROWN: RGBA_VALUES = 181, 136, 64
    LIGHT_GREEN: RGBA_VALUES = 133, 153, 75
    TURQUOISE: RGBA_VALUES = 40, 161, 151

    @property
    def rgba_value(self) -> tuple[int, int, int, int]:
        value: tuple[int, int, int] = self.value
        return value[0], value[1], value[2], 1

    @property
    def presentation_name(self) -> str:
        name = (
            self.name.split(sep="_", maxsplit=2)[2]
            if self.name.startswith("COLOUR_")
            else self.name
        )

        return self._convert_to_readable_name(name=name).lower()

    @classmethod
    def _convert_to_readable_name(cls, name: str) -> str:
        return " ".join(name.split("_")).title()

    @property
    def stringified(self) -> str:
        return f"rgba{self.rgba_value}"

    @classmethod
    def choices(cls):
        return tuple(
            (
                chart_line_color.name,
                cls._convert_to_readable_name(chart_line_color.name),
            )
            for chart_line_color in cls
        )

    @classmethod
    def selectable_choices(cls):
        """Returns chart line colours which are selectable from the CMS

        Returns:
            Nested tuples of 2 item tuples as expected by the CMS forms
            with the value name and a formatted display version
            Examples:
                (("COLOUR_1_DARK_BLUE", "Colour 1 Dark Blue"), ...)
        """
        non_selectable = [
            cls.TREND_LINE_NEGATIVE,
            cls.TREND_LINE_POSITIVE,
            cls.TREND_LINE_NEUTRAL,
        ]
        return tuple(
            (
                chart_line_color.name,
                cls._convert_to_readable_name(chart_line_color.name),
            )
            for chart_line_color in cls
            if chart_line_color not in non_selectable
        )

    @classmethod
    def get_colour(cls, *, colour: str) -> "RGBAChartLineColours":
        try:
            return cls[colour]
        except KeyError:
            return cls.COLOUR_1_DARK_BLUE


class RGBAColours(Enum):
    # Used for the line plot
    BLACK: RGBA_VALUES = 0, 0, 0, 1

    # Used for the background
    WHITE: RGBA_VALUES = 0, 0, 0, 0
    DARK_BLUE_GREY: RGBA_VALUES = 107, 114, 118, 1

    # --------------------
    # Line chart specific
    # --------------------

    # Used for the main background colour (in Line charts)
    LINE_LIGHT_GREY: RGBA_VALUES = 248, 248, 248, 1

    # Used for the shaded filled region underneath the line plot (in Line charts)
    LINE_DARK_GREY: RGBA_VALUES = 243, 242, 241, 1

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
