from unittest import mock

import pytest

from metrics.interfaces.charts import validation


def test_validate_series_type_chart_works_with_metric():
    """
    Given a metric of `new_cases_daily` and a request for a `simple_line` type chart
    When `_validate_series_type_chart_works_with_metric()` is called from an instance of `ChartsRequestValidator`
    Then None is returned
    """
    # Given
    metric = "new_cases_daily"
    chart_type = "simple_line"
    mocked_core_time_series_manager = mock.Mock()
    mocked_core_time_series_manager.get_count.return_value = 10

    validator = validation.ChartsRequestValidator(
        topic=mock.Mock(),
        metric=metric,
        chart_type=chart_type,
        date_from=mock.Mock(),
        core_time_series_manager=mocked_core_time_series_manager
    )

    # When
    validated = validator._validate_series_type_chart_works_with_metric()

    # Then
    assert validated is None


def test_validate_series_type_chart_works_with_metric_raises_error():
    """
    Given a metric of `covid_occupied_beds_latest` and a request for a `simple_line` type chart
    When `_validate_series_type_chart_works_with_metric()` is called from an instance of `ChartsRequestValidator`
    Then a `ChartTypeDoesNotSupportMetricError` is raised
    """
    # Given
    metric = "covid_occupied_beds_latest"
    chart_type = "simple_line"
    mocked_core_time_series_manager = mock.Mock()
    mocked_core_time_series_manager.get_count.return_value = 1

    validator = validation.ChartsRequestValidator(
        topic=mock.Mock(),
        metric=metric,
        chart_type=chart_type,
        date_from=mock.Mock(),
        core_time_series_manager=mocked_core_time_series_manager
    )

    # When / Then
    expected_error_message = f"`{metric}` is not compatible with `{chart_type}` chart types"
    with pytest.raises(validation.ChartTypeDoesNotSupportMetricError, match=expected_error_message):
        validator._validate_series_type_chart_works_with_metric()
