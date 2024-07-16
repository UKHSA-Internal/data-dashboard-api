def validate_in_reporting_delay_period(
    *, in_reporting_delay_period_values: list[bool]
) -> None:
    """Validates the `in_reporting_delay_period_values` only contains trailing True values

    Args:
        in_reporting_delay_period_values: List of booleans
            which represent the in reporting delay period values
            associated with each timeseries

    Returns:
        None

    Raises:
        `ValueError`: If there are any True values
            in the leading section of the list.

    """
    if True not in in_reporting_delay_period_values:
        return

    first_true_index = in_reporting_delay_period_values.index(True)
    is_valid: bool = all(in_reporting_delay_period_values[first_true_index:])
    if is_valid:
        return

    raise ValueError
