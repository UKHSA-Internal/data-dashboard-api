def validate_headline_data(data: list["InboundHeadlineSpecificFields"]):
    """Validates the `data` field to check it conforms to the expected rules

    Notes:
        There must be only 1 `InboundHeadlineSpecificFields` model.
        If there is either no data point or multiple data points,
        then the validation checks will fail.

    Args:
        data: The `data` field value being validated

    Returns:
        The input `data` unchanged if
        it has passed the validation checks.

    Raises:
        `ValueError`: If any of the validation checks fail

    """
    return _validate_single_data_point_only(data=data)


def _validate_single_data_point_only(
    data: list["InboundHeadlineSpecificFields"],
) -> list["InboundHeadlineSpecificFields"]:
    if len(data) != 1:
        raise ValueError
    return data
