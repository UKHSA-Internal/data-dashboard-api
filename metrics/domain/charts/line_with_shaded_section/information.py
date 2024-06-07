from metrics.domain.charts.colour_scheme import RGBAColours
from metrics.domain.charts.type_hints import COLOUR_PAIR
from metrics.domain.common.information import is_metric_improving


def _get_line_and_fill_colours(
    *,
    metric_is_improving: bool,
) -> tuple[RGBAColours, RGBAColours]:
    if metric_is_improving:
        return RGBAColours.LS_DARK_GREEN, RGBAColours.LS_LIGHT_GREEN
    return RGBAColours.DARK_RED, RGBAColours.LIGHT_RED


def determine_line_and_fill_colours(
    *, change_in_metric_value: int, metric_name: str
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
