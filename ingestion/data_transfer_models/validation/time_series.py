from ingestion.metrics_interface.interface import MetricsAPIInterface
from ingestion.utils.dates import calculate_days_between_dates


def validate_time_series(
    time_series: list["InboundTimeSeriesSpecificFields"], metric_frequency: str
) -> list["InboundTimeSeriesSpecificFields"]:
    """Validates the `time_series` value to check it conforms to expected rules

    Notes:
        If the `metric_frequency` is "D" (daily),
        then each `time_series` must 1 day apart.
        If the `metric_frequency` is "W" (weekly),
        then each `time_series` must be 7 days apart.
        If the above rules do not hold true where relevant,
        then the validation checks will fail.

    Args:
        time_series: List of enriched `InboundTimeSeriesSpecificFields`
            models containing `date` and metric values
            for the individual time series records
        metric_frequency: The selected metric frequency
            which had been provided from the payload to
            the `InboundTimeSeriesSpecificFields` model

    Returns:
        The list of enriched `InboundTimeSeriesSpecificFields`
        unchanged if all validation checks passed

    Raises:
        `ValueError`: If any of the validation checks fail

    """
    time_period_enum = MetricsAPIInterface.get_time_period_enum()

    if metric_frequency == time_period_enum.Daily.value:
        return _validate_data_points_are_daily(time_series=time_series)

    if metric_frequency == time_period_enum.Weekly.value:
        return _validate_data_points_are_weekly(time_series=time_series)

    raise ValueError


def _validate_data_points_are_daily(
    time_series: list["InboundTimeSeriesSpecificFields"],
) -> list["InboundTimeSeriesSpecificFields"]:
    dates = [record.date for record in time_series]

    differences = calculate_days_between_dates(dates=dates)
    if differences == {1}:
        return time_series

    raise ValueError


def _validate_data_points_are_weekly(
    time_series: list["InboundTimeSeriesSpecificFields"],
) -> list["InboundTimeSeriesSpecificFields"]:

    dates = [record.date for record in time_series]

    differences = calculate_days_between_dates(dates=dates)
    if differences == {7}:
        return time_series

    raise ValueError
