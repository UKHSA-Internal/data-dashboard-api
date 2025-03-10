from enum import Enum

DEFAULT_CHART_HEIGHT = 220
DEFAULT_CHART_WIDTH = 515
DEFAULT_METRIC_VALUE_ERROR = "The metric provided doesn't appear to be valid."
DEFAULT_METRIC_GROUP_VALUE_ERROR = (
    "The metric_group provided doesn't appear to be valid."
)


def _check_for_substring_match(
    *, string_to_check: str, substrings: tuple[str, ...]
) -> bool:
    return any(sub_string in string_to_check.lower() for sub_string in substrings)


class ChartTypes(Enum):
    simple_line = "simple_line"
    waffle = "waffle"
    line_with_shaded_section = "line_with_shaded_section"
    bar = "bar"
    line_multi_coloured = "line_multi_coloured"
    line_single_simplified = "line_single_simplified"

    @classmethod
    def choices(cls) -> tuple[tuple[str, str], ...]:
        return tuple((chart_type.value, chart_type.value) for chart_type in cls)

    @classmethod
    def selectable_choices(cls) -> tuple[tuple[str, str], ...]:
        """Returns chart types which are selectable from the CMS as a nested tuple of 2-item tuples.

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("line_with_shaded_section", "line_with_shaded_section"), ...)

        """
        selectable = (
            cls.line_multi_coloured,
            cls.bar,
            cls.line_with_shaded_section,
            cls.line_single_simplified,
        )
        return tuple((chart_type.value, chart_type.value) for chart_type in selectable)

    @classmethod
    def selectable_headline_choices(cls) -> tuple[tuple[str, str], ...]:
        """Returns chart types which are selectable from the CMS as a nested tuple of 2-item tuples.

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("bar", "bar"), ...)

        """
        selectable = (cls.bar,)
        return tuple((chart_type.value, chart_type.value) for chart_type in selectable)

    @classmethod
    def selectable_simplified_chart_choices(cls) -> tuple[tuple[str, str], ...]:
        """Returns chart types which are selectable from the CMS as nested tuple of 2-item tuples.

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("line_single_simplified", "line_single_simplified"), ...)
        """
        selectable = (cls.line_single_simplified,)
        return tuple((chart_type.value, chart_type.value) for chart_type in selectable)

    @classmethod
    def values(cls) -> list[str]:
        return [chart_type.value for chart_type in cls]


class ChartAxisFields(Enum):
    stratum = "stratum__name"
    age = "age__name"
    date = "date"
    metric = "metric_value"
    geography = "geography__name"
    sex = "sex"

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
    def get_x_axis_value(cls, *, name: str) -> str:
        try:
            return cls[name].value
        except KeyError:
            return cls.get_default_x_axis().value

    @classmethod
    def get_default_y_axis(cls):
        return cls.metric

    @classmethod
    def get_y_axis_value(cls, *, name: str) -> str:
        try:
            return cls[name].value
        except KeyError:
            return cls.get_default_y_axis().value


DEFAULT_X_AXIS = ChartAxisFields.get_default_x_axis().name
DEFAULT_Y_AXIS = ChartAxisFields.get_default_y_axis().name
DEFAULT_Y_AXIS_MINIMUM_VAlUE = 0


class DataSourceFileType(Enum):
    # Headline types
    headline = "headline"

    # Timeseries types
    cases = "cases"
    deaths = "deaths"
    healthcare = "healthcare"
    testing = "testing"
    vaccinations = "vaccinations"
    syndromic = "syndromic"

    @property
    def is_headline(self) -> bool:
        return self.value == "headline"

    @property
    def is_timeseries(self) -> bool:
        return self.value != "headline"


def extract_metric_group_from_metric(metric: str) -> str | None:
    """Returns the metric group based on the provided metric

    Args:
        metric: string representation a metric

    Returns:
        string of the metric group the provided metric belongs to
        if no matching metric group is found then a `ValueError` is
        raised due to an invalid metric value.
    """
    if DataSourceFileType.headline.value in metric:
        return DataSourceFileType.headline.value

    for metric_group in DataSourceFileType:
        if metric_group.value in metric:
            return metric_group.value

    raise ValueError(DEFAULT_METRIC_VALUE_ERROR)
