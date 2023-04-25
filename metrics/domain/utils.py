from enum import Enum
from typing import List


def _check_for_substring_match(string_to_check: str, substrings: List[str]) -> bool:
    return any((sub_string in string_to_check for sub_string in substrings))


class ChartTypes(Enum):
    simple_line = "simple_line"
    waffle = "waffle"
    line_with_shaded_section = "line_with_shaded_section"
    bar = "bar"

    @classmethod
    def choices(cls):
        return tuple((chart_type.value, chart_type.value) for chart_type in cls)

    @classmethod
    def values(cls):
        return [chart_type.value for chart_type in cls]
