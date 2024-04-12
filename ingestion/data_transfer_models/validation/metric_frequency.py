from ingestion.metrics_interface.interface import MetricsAPIInterface


def validate_metric_frequency(metric_frequency: str) -> str:
    """Casts the `metric_frequency` value to one of the expected values

    Notes:
        Expected values are dictated by the `TimePeriod` enum

    Returns:
        A string representation of the parsed metric_frequency value

    Raises:
        `ValueError`: If the `metric_frequency` does not
            conform to one of the expected values

    """
    time_period_enum = MetricsAPIInterface.get_time_period_enum()
    try:
        selected_enum = time_period_enum[metric_frequency.title()]
    except KeyError as error:
        raise ValueError from error

    return selected_enum.value
