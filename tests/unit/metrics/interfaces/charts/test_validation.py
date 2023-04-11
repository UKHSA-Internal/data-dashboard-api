import datetime
from unittest import mock

import pytest

from metrics.interfaces.charts import validation
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.models.core_time_series_factory import FakeCoreTimeSeriesFactory


class TestValidateSeriesChartTypeWorksWithMetric:
    def test_can_validate_successfully(self):
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
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # When
        validated = validator._validate_series_type_chart_works_with_metric()

        # Then
        assert validated is None

    def test_can_raise_error_for_invalidate_combination(self):
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
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # When / Then
        expected_error_message = (
            f"`{metric}` is not compatible with `{chart_type}` chart types"
        )
        with pytest.raises(
            validation.ChartTypeDoesNotSupportMetricError, match=expected_error_message
        ):
            validator._validate_series_type_chart_works_with_metric()


class TestDoesMetricHaveMultipleRecords:
    def test_returns_true_for_multiple_records(self):
        """
        Given a metric and a topic which match multiple records
        When `does_metric_have_multiple_records()` is called from an instance of `ChartsRequestValidator`
        Then True is returned
        """
        # Given
        time_series = FakeCoreTimeSeriesFactory.build_example_covid_time_series_range()
        metric_name = time_series[0].metric.name
        topic_name = time_series[0].metric.topic.name
        date_from = datetime.date(2020, 1, 1)

        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=time_series
        )

        validator = validation.ChartsRequestValidator(
            topic=topic_name,
            metric=metric_name,
            chart_type=mock.Mock(),
            date_from=date_from,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        metric_has_multiple_records: bool = (
            validator.does_metric_have_multiple_records()
        )

        # Then
        assert metric_has_multiple_records

    def test_returns_false_for_single_record(self):
        """
        Given a metric of `weekly_positivity` and a topic of `Influenza`
        And only one matching record alongside a number of records which do not match
        When `does_metric_have_multiple_records()` is called from an instance of `ChartsRequestValidator`
        Then False is returned
        """
        # Given
        metric_name = "weekly_positivity"
        topic_name = "Influenza"
        date_from = datetime.date(2022, 1, 1)

        matching_record = FakeCoreTimeSeriesFactory.build_time_series(
            dt=date_from, metric_name=metric_name, topic_name=topic_name
        )
        time_series = [
            *FakeCoreTimeSeriesFactory.build_example_covid_time_series_range(),
            matching_record,
        ]
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=time_series
        )

        validator = validation.ChartsRequestValidator(
            topic=topic_name,
            metric=metric_name,
            chart_type=mock.Mock(),
            date_from=date_from,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        metric_has_multiple_records: bool = (
            validator.does_metric_have_multiple_records()
        )

        # Then
        assert not metric_has_multiple_records

    def test_returns_false_for_non_existent_record(self):
        """
        Given a metric and a topic for a record which does not exist
        When `does_metric_have_multiple_records()` is called from an instance of `ChartsRequestValidator`
        Then False is returned
        """
        # Given
        metric_name = "non_existent_metric_name"
        topic_name = "non_existent_topic_name"
        date_from = datetime.date(2022, 1, 1)

        time_series = FakeCoreTimeSeriesFactory.build_example_covid_time_series_range()
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=time_series
        )

        validator = validation.ChartsRequestValidator(
            topic=topic_name,
            metric=metric_name,
            chart_type=mock.Mock(),
            date_from=date_from,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        metric_has_multiple_records: bool = (
            validator.does_metric_have_multiple_records()
        )

        # Then
        assert not metric_has_multiple_records
