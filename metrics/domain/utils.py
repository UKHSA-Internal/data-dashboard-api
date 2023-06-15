from enum import Enum
from typing import List

DEFAULT_CHART_HEIGHT = 220
DEFAULT_CHART_WIDTH = 435


def _check_for_substring_match(string_to_check: str, substrings: List[str]) -> bool:
    return any((sub_string in string_to_check for sub_string in substrings))


class ChartTypes(Enum):
    simple_line = "simple_line"
    waffle = "waffle"
    line_with_shaded_section = "line_with_shaded_section"
    bar = "bar"
    line_multi_coloured = "line_multi_coloured"

    @classmethod
    def choices(cls):
        return tuple((chart_type.value, chart_type.value) for chart_type in cls)

    @classmethod
    def values(cls):
        return [chart_type.value for chart_type in cls]


class ChartAxisFields(Enum):
    stratum = "stratum__name"
    date = "dt"
    metric = "metric_value"
    geography = "geography__geography_type__name"

    @classmethod
    def choices(cls):
        return tuple((field_name.value, field_name.name) for field_name in cls)

    @classmethod
    def values(cls):
        return tuple(field_name.value for field_name in cls)

    def __str__(self):
        return str(self.value)


def get_axis_name(field_name: str):
    """Convert the given field_name into the "display" version
    If no conversion is required then just return the supplied argument unaltered

    Args:
        field_name: The fieldname to convert to the display version if required

    Returns:
        The converted or unaltered fieldname
    """
    return (
        ChartAxisFields(field_name).name
        if field_name in ChartAxisFields.values()
        else field_name
    )


DEFAULT_X_AXIS = ChartAxisFields.date.value
DEFAULT_Y_AXIS = ChartAxisFields.metric.value
