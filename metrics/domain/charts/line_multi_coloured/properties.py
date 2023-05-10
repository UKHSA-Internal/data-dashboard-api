from enum import Enum


class ChartLineTypes(Enum):
    SOLID = "solid"
    DASH = "dash"

    @classmethod
    def choices(cls):
        return tuple((chart_type.name, chart_type.name) for chart_type in cls)

    @classmethod
    def get_chart_line_type(cls, line_type: str) -> "ChartLineTypes":
        try:
            return cls[line_type]
        except KeyError:
            return cls.SOLID
