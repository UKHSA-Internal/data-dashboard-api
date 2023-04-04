import logging
from typing import List, Tuple

from metrics.domain.charts import type_hints
from metrics.domain.charts.line_with_shaded_section import colour_scheme

logger = logging.getLogger(__name__)


def determine_line_and_fill_colours(
    change_in_metric_value: int, metric_name: str
) -> type_hints.COLOUR_PAIR:
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

    return colour_scheme._get_line_and_fill_colours(
        metric_is_improving=metric_is_improving
    )


def _calculate_mean(values: List[int]) -> float:
    return sum(values) / len(values)


def get_metric_state(change_in_metric_value: float, metric_name: str) -> int:
    """Returns metric state.
    1 = positive change
    0 = no change
    -1 = negative change
    """
    if change_in_metric_value == 0:
        return 0

    return (
        1
        if is_metric_improving(
            change_in_metric_value=change_in_metric_value, metric_name=metric_name
        )
        else -1
    )


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
            E.g. new_admissions_daily

    Returns:
        bool: True if the change in value is to be considered
            positive relative to that metric. False otherwise.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    increasing_is_bad = (
        "cases",
        "deaths",
        "admission",
        "covid_occupied",
        "positivity",
    )
    increasing_is_good = ("vaccines", "vaccination", "vaccinated", "tests", "pcr")

    if _check_for_substring_match(
        string_to_check=metric_name, substrings=increasing_is_bad
    ):
        return change_in_metric_value < 0

    if _check_for_substring_match(
        string_to_check=metric_name, substrings=increasing_is_good
    ):
        return change_in_metric_value > 0

    raise ValueError(f"{metric_name} is not supported")


def _check_for_substring_match(string_to_check: str, substrings: List[str]) -> bool:
    return any((sub_string in string_to_check for sub_string in substrings))
