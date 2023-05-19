from enum import Enum, StrEnum
from typing import List


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


class GraphAxisFields(StrEnum):
    stratum = "stratum__name"
    date = "dt"
    metric = "metric_value"
    geography = "geography__geography_type__name"

    @classmethod
    def choices(cls):
        return tuple((field_name.name, field_name.name) for field_name in cls)
