from datetime import date, timedelta
from enum import Enum

DEFAULT_CHART_HEIGHT = 220
DEFAULT_CHART_WIDTH = 515


def get_last_day_of_month(date: date) -> date:
    next_month = date.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def _check_for_substring_match(
    string_to_check: str, substrings: tuple[str, ...]
) -> bool:
    return any(sub_string in string_to_check.lower() for sub_string in substrings)


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
    age = "age__name"
    date = "date"
    metric = "metric_value"
    geography = "geography__geography_type__name"

    @classmethod
    def choices(cls):
        return tuple((field_name.name, field_name.name) for field_name in cls)

    @classmethod
    def values(cls):
        return tuple(field_name.value for field_name in cls)

    def __str__(self):
        return str(self.value)

    @classmethod
    def get_default_x_axis(cls):
        return cls.date

    @classmethod
    def get_x_axis_value(cls, name: str) -> str:
        try:
            return cls[name].value
        except KeyError:
            return cls.get_default_x_axis().value

    @classmethod
    def get_default_y_axis(cls):
        return cls.metric

    @classmethod
    def get_y_axis_value(cls, name: str) -> str:
        try:
            return cls[name].value
        except KeyError:
            return cls.get_default_y_axis().value


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


DEFAULT_X_AXIS = ChartAxisFields.get_default_x_axis().name
DEFAULT_Y_AXIS = ChartAxisFields.get_default_y_axis().name
