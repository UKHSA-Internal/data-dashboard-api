from datetime import date, timedelta
from enum import Enum
from typing import List

DEFAULT_CHART_HEIGHT = 220
DEFAULT_CHART_WIDTH = 435


def get_last_day_of_month(dt: date) -> date:
    next_month = dt.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


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
    return (
        ChartAxisFields(field_name).name
        if field_name in ChartAxisFields.values()
        else field_name
    )


DEFAULT_X_AXIS = ChartAxisFields.date.value
DEFAULT_Y_AXIS = ChartAxisFields.metric.value
