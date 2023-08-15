from metrics.domain.charts.colour_scheme import RGBAColours
from metrics.domain.charts.type_hints import COLOUR_PAIR
from metrics.domain.utils import _check_for_substring_match


def _get_line_and_fill_colours(
    metric_is_improving: bool,
) -> tuple[RGBAColours, RGBAColours]:
    if metric_is_improving:
        return RGBAColours.LS_DARK_GREEN, RGBAColours.LS_LIGHT_GREEN
    return RGBAColours.DARK_RED, RGBAColours.LIGHT_RED


def determine_line_and_fill_colours(
    change_in_metric_value: int, metric_name: str
) -> COLOUR_PAIR:
    """Returns colours dependening on whether the `change_in_metric_value` is considered to be good.

    For example, for cases or deaths, an average increase in the `change_in_metric_value`
    would be considered to be negative. Which would return a pair of red colours.
    But, for vaccinations an increase in the corresponding average change
    would be considered to be positive. Which would return a pair of green colours.

    Examples:
        >>> determine_line_and_fill_colours(change_in_metric_value=-2, metric_name='new_cases_daily')
        (colour_scheme.RGBAColours.DARK_GREEN, colour_scheme.RGBAColours.LIGHT_GREEN)

        >>> is_metric_improving(change_in_metric_value=2, metric_name='new_cases_daily')
        (colour_scheme.RGBAColours.DARK_RED, colour_scheme.RGBAColours.LIGHT_RED)

    Args:
        change_in_metric_value: The change in metric value from the last 7 days
            compared to the preceding 7 days.
        metric_name: The associated metric_name,
            E.g. new_admissions_daily

    Returns:
        Tuple[colour_scheme.RGBAColours, colour_scheme.RGBAColours]:
            A pair of colours depending on whether
            the analysed slice is considered to be
            a good thing or a bad thing.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    metric_is_improving = is_metric_improving(
        change_in_metric_value=change_in_metric_value,
        metric_name=metric_name,
    )

    return _get_line_and_fill_colours(metric_is_improving=metric_is_improving)


def is_metric_improving(change_in_metric_value: float, metric_name: str) -> bool:
    """Checks whether a positive or negative `change_in_metric_value` should be considered a good thing.

    For example, for cases or deaths, an increase in metric value
    would be considered to be negative.
    But, for vaccinations an increase in the corresponding metric value
    would be considered to be positive.

    Examples:
        >>> is_metric_improving(change_in_metric_value=20, metric_name='new_cases_daily')
        False

        >>> is_metric_improving(change_in_metric_value=-20, metric_name='new_cases_daily')
        True

    Args:
        `change_in_metric_value`: The change in metric value,
            as a number. E.g. -10
        `metric_name`: The associated metric_name,
            E.g. `new_admissions_daily`

    Returns:
        bool: True if the change in value is to be considered
            positive relative to that metric. False otherwise.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    increasing_is_bad: tuple[str, ...] = (
        "cases",
        "deaths",
        "admission",
        "occupied",
        "positivity",
    )
    increasing_is_good: tuple[str, ...] = (
        "vaccines",
        "vaccination",
        "vaccinated",
        "tests",
        "pcr",
    )

    if _check_for_substring_match(
        string_to_check=metric_name, substrings=increasing_is_bad
    ):
        return change_in_metric_value < 0

    if _check_for_substring_match(
        string_to_check=metric_name, substrings=increasing_is_good
    ):
        return change_in_metric_value > 0

    raise ValueError(f"{metric_name} is not supported")
