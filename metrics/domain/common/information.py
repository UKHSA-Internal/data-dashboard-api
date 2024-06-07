from metrics.domain.common.utils import _check_for_substring_match


class TrendMetricNotSupportedError(Exception):
    def __init__(self, metric_name: str):
        message = f"{metric_name} is not supported"
        super().__init__(message)


def is_metric_improving(*, change_in_metric_value: float, metric_name: str) -> bool:
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
        `TrendMetricNotSupportedError`: If the `metric_name`
            is not supported.

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

    raise TrendMetricNotSupportedError(metric_name=metric_name)
