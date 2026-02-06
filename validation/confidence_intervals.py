UPPER_CONFIDENCE_LOWER_THAN_METRIC_MESSAGE = (
    "The upper_confidence value was lower than the metric"
)

LOWER_CONFIDENCE_HIGHER_THAN_METRIC_MESSAGE = (
    "The lower_confidence value was higher than the metric"
)

UPPER_CONFIDENCE_LOWER_THAN_LOWER_CONFIDENCE_MESSAGE = (
    "The upper_confidence value was lower than the lower_confidence"
)

UPPER_CONFIDENCE_BUT_NO_LOWER_CONFIDENCE_MESSAGE = (
    "upper_confidence has been provided but no lower_confidence"
)


def validate_confidence_intervals(
    upper_confidence: float, lower_confidence: float, metric_value: float
):
    """Checks that the rules for confidence values are followed

    Args:
       self: the model to be validated

    Returns:
       True if upper_confidence > metric_value > lower_confidence
       False if not

    Raises:
        `ValidationError`: If any of the validation checks fail

    """
    if upper_confidence is None and lower_confidence is None:
        return True

    if lower_confidence is None:
        raise ValueError(
            UPPER_CONFIDENCE_BUT_NO_LOWER_CONFIDENCE_MESSAGE,
            {upper_confidence, lower_confidence, metric_value},
        )

    if upper_confidence < lower_confidence:
        raise ValueError(
            UPPER_CONFIDENCE_LOWER_THAN_LOWER_CONFIDENCE_MESSAGE,
            {upper_confidence, lower_confidence, metric_value},
        )
    if upper_confidence < metric_value:
        raise ValueError(
            UPPER_CONFIDENCE_LOWER_THAN_METRIC_MESSAGE,
            {upper_confidence, lower_confidence, metric_value},
        )

    if lower_confidence > metric_value:
        raise ValueError(
            LOWER_CONFIDENCE_HIGHER_THAN_METRIC_MESSAGE,
            {upper_confidence, lower_confidence, metric_value},
        )

    return True
