def validate_metric(metric: str, metric_group: str) -> str:
    """Validates the `metric` value to check it conforms to the accepted format

    Args:
        metric: The name of the `metric` being checked
        metric_group: The metric group which was
            included in the payload alongside the metric

    Returns:
        The input `metric_group` unchanged if
        it has passed the validation checks.

    Raises:
         `ValueError`: If any of the validation checks fail

    """
    return _validate_metric_group_in_metric(metric=metric, metric_group=metric_group)


def _validate_metric_group_in_metric(metric: str, metric_group: str) -> str:
    try:
        if metric_group in metric:
            return metric
    except TypeError:
        raise ValueError

    raise ValueError
