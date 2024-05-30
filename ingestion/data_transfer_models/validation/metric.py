MINIMUM_METRIC_SECTION_COUNT = 3
METRIC_STRUCTURE_VALIDATION_ERROR = "Invalid metric format."
METRIC_GROUP_VALIDATION_ERROR = "Metric group is not valid for this metric."
TOPIC_NAME_VALIDATION_ERROR = "The topic name is not valid for this metric."
METRIC_DETAIL_VALIDATION_ERROR = "Invalid metric, contains special characters."


def validate_metric(*, metric: str, metric_group: str, topic: str) -> str:
    """Validates the `metric` value to check it conforms to the accepted format

    Args:
        metric: The name of the `metric` being checked
        metric_group: The metric group which was
            included in the payload alongside the metric
        topic: The topic which was included in the payload
            alongside the metric

    Returns:
        The input `metric` unchanged if
        it has passed the validation checks.

    Raises:
         `ValueError`: If any of the validation checks fail
    """
    _validate_metric_structure(metric=metric)
    _validate_topic_in_metric(metric=metric, topic=topic)
    _validate_metric_group_in_metric(metric=metric, metric_group=metric_group)

    return metric


def _validate_metric_structure(*, metric: str) -> None:
    """Split metric string into sections and validates metric structure.
        There should be at least 3 parts. `<topic>_<metric_group>_<metric_detail>`
        and the metric_detail should be alphanumeric.

    Args:
        metric: the current metric provided as a string

    Returns:
        None
    """
    metric_sections = metric.split("_")

    if len(metric_sections) < MINIMUM_METRIC_SECTION_COUNT:
        raise ValueError(METRIC_STRUCTURE_VALIDATION_ERROR)

    if not "".join(metric_sections[2:]).isalnum():
        raise ValueError(METRIC_STRUCTURE_VALIDATION_ERROR)


def _validate_topic_in_metric(*, metric: str, topic: str) -> None:
    """Checks that the provided `topic` is in the `metric` name.
        This check is made case insensitive because some topic names
        are capitalised.

    Args:
        metric: The name of the metric being checked
        topic: The `topic` provided in the payload that
            the metric is being checked against.

    Returns:
        None
    """
    try:
        if topic.lower() not in metric.lower():
            raise ValueError(TOPIC_NAME_VALIDATION_ERROR)
    except (AttributeError, TypeError):
        raise ValueError(TOPIC_NAME_VALIDATION_ERROR)


def _validate_metric_group_in_metric(*, metric: str, metric_group: str) -> None:
    """Checks that the `metric` contains the provided `metric_group`

    Args:
        metric: The name of the metric being checked
        metric_group: The `metric_group` provided in the payload that
            the metric is being checked against.

    Returns:
        None
    """
    try:
        if metric_group not in metric:
            raise ValueError(METRIC_GROUP_VALIDATION_ERROR)
    except (AttributeError, TypeError):
        raise ValueError(METRIC_GROUP_VALIDATION_ERROR)
