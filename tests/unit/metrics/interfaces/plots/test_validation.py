import datetime
from unittest import mock

import pytest

from metrics.domain.models import PlotParameters
from metrics.domain.utils import ChartTypes
from metrics.interfaces.plots import validation
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager

EXPECTED_DATE_FORMAT: str = "%Y-%m-%d"


@pytest.fixture
def valid_plot_parameters() -> PlotParameters:
    return PlotParameters(
        metric="new_cases_daily",
        topic="COVID-19",
        chart_type=ChartTypes.simple_line.value,
        date_from="2022-01-01",
    )


class TestValidate:
    @mock.patch.object(validation.PlotValidation, "_validate_dates")
    @mock.patch.object(
        validation.PlotValidation, "_validate_metric_is_available_for_topic"
    )
    @mock.patch.object(
        validation.PlotValidation,
        "_validate_series_type_chart_works_with_metric",
    )
    def test_delegates_to_correct_validators(
        self,
        spy_validate_series_type_chart_works_with_metric: mock.MagicMock,
        spy_validate_metric_is_available_for_topic: mock.MagicMock,
        spy_validate_dates: mock.MagicMock,
    ):
        """
        Given an instance of the `PlotValidation` class
        When `validate()` is called
        Then the correct sub validate methods are called and delegated to
        """
        # Given
        validator = validation.PlotValidation(
            plot_parameters=mock.Mock(),
            core_time_series_manager=mock.Mock(),
            metric_manager=mock.Mock(),
        )

        # When
        validator.validate()

        # Then
        spy_validate_series_type_chart_works_with_metric.assert_called_once()
        spy_validate_metric_is_available_for_topic.assert_called_once()
        spy_validate_dates.assert_called_once()


class TestValidateSeriesChartTypeWorksWithMetric:
    def test_can_validate_successfully(self, valid_plot_parameters: PlotParameters):
        """
        Given a valid `PlotParameters` model
        When `_validate_series_type_chart_works_with_metric()` is called from an instance of `PlotValidation`
        Then None is returned
        """
        # Given
        mocked_core_time_series_manager = mock.Mock()
        mocked_core_time_series_manager.get_count.return_value = 10

        validator = validation.PlotValidation(
            plot_parameters=valid_plot_parameters,
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # When
        validated = validator._validate_series_type_chart_works_with_metric()

        # Then
        assert validated is None

    def test_passes_naively_if_non_series_chart_type_provided(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given a valid `PlotParameters` model and a request for a `waffle` type chart
        When `_validate_series_type_chart_works_with_metric()` is called from an instance of `PlotValidation`
        Then None is returned
        """
        # Given
        valid_plot_parameters.chart_type = ChartTypes.waffle.value

        validator = validation.PlotValidation(
            plot_parameters=valid_plot_parameters,
        )

        # When
        validated = validator._validate_series_type_chart_works_with_metric()

        # Then
        assert validated is None

    def test_can_raise_error_for_invalid_combination(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given an otherwise valid `PlotParameters` model which has a metric of `covid_occupied_beds_latest`
        And a request for a `simple_line` type chart
        When `_validate_series_type_chart_works_with_metric()` is called from an instance of `PlotValidation`
        Then a `ChartTypeDoesNotSupportMetricError` is raised
        """
        # Given
        plot_parameters: PlotParameters = valid_plot_parameters
        metric = "covid_occupied_beds_latest"
        chart_type = ChartTypes.simple_line.value
        plot_parameters.metric = metric
        plot_parameters.chart_type = chart_type

        mocked_core_time_series_manager = mock.Mock()
        mocked_core_time_series_manager.get_count.return_value = 1

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
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


class TestValidateMetricIsAvailableForTopic:
    def test_can_validate_successfully(self, valid_plot_parameters: PlotParameters):
        """
        Given an otherwise valid `PlotParameters` model which has a metric of `covid_occupied_beds_latest`
        And a topic of `COVID-19` which is valid
        When `_validate_metric_is_available_for_topic()` is called from an instance of `PlotValidation`
        Then None is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        metric_name = "covid_occupied_beds_latest"
        valid_topic_name = "COVID-19"
        plot_parameters.metric = metric_name
        plot_parameters.topic = valid_topic_name

        metrics = [
            FakeMetricFactory.build_example_metric(
                metric_name=metric_name, topic_name=valid_topic_name
            )
        ] * 3
        fake_metric_manager = FakeMetricManager(metrics=metrics)

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
            metric_manager=fake_metric_manager,
        )

        # When
        validated = validator._validate_metric_is_available_for_topic()

        # Then
        assert validated is None

    def test_can_raise_error_for_invalid_combination(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given an otherwise valid `PlotParameters` model which has a metric of `covid_occupied_beds_latest`
        And a topic of `Influenza` which is invalid
        When `_validate_metric_is_available_for_topic()` is called from an instance of `PlotValidation`
        Then a `MetricDoesNotSupportTopicError` is raised
        """
        # Given
        plot_parameters = valid_plot_parameters
        metric_name = "covid_occupied_beds_latest"
        invalid_topic_name = "Influenza"
        plot_parameters.metric = metric_name
        plot_parameters.topic = invalid_topic_name

        plot_parameters = PlotParameters(
            metric=metric_name,
            topic=invalid_topic_name,
            chart_type=ChartTypes.simple_line.value,
            date_from="2023-01-01",
        )

        metrics = [
            FakeMetricFactory.build_example_metric(
                metric_name=metric_name, topic_name="COVID-19"
            )
        ] * 3
        fake_metric_manager = FakeMetricManager(metrics=metrics)

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
            metric_manager=fake_metric_manager,
        )

        # When / Then
        expected_error_message = f"`{invalid_topic_name}` does not have a corresponding metric of `{metric_name}`"
        with pytest.raises(
            validation.MetricDoesNotSupportTopicError, match=expected_error_message
        ):
            validator._validate_metric_is_available_for_topic()


class TestDoesMetricHaveMultipleRecords:
    def test_returns_true_for_multiple_records(self):
        """
        Given a `metric_name` and a `topic_name` which match multiple records
        When `does_metric_have_multiple_records()` is called from an instance of `PlotValidation`
        Then True is returned
        """
        # Given
        time_series = FakeCoreTimeSeriesFactory.build_example_covid_time_series_range()
        metric_name = time_series[0].metric.name
        topic_name = time_series[0].metric.topic.name
        date_from = "2020-01-01"
        plot_parameters = PlotParameters(
            metric=metric_name,
            topic=topic_name,
            chart_type=ChartTypes.simple_line.value,
            date_from=date_from,
        )

        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=time_series
        )

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        metric_has_multiple_records: bool = (
            validator._does_metric_have_multiple_records()
        )

        # Then
        assert metric_has_multiple_records

    def test_returns_false_for_single_record(self):
        """
        Given a metric of `weekly_positivity` and a topic of `Influenza`
        And only one matching record alongside a number of records which do not match
        When `does_metric_have_multiple_records()` is called from an instance of `PlotValidation`
        Then False is returned
        """
        # Given
        metric_name = "weekly_positivity"
        topic_name = "Influenza"
        date_from = datetime.date(year=2022, month=1, day=1)
        plot_parameters = PlotParameters(
            metric=metric_name,
            topic=topic_name,
            chart_type=ChartTypes.simple_line.value,
            date_from=date_from.strftime(EXPECTED_DATE_FORMAT),
        )

        matching_record = FakeCoreTimeSeriesFactory.build_time_series(
            dt=date_from,
            metric_name=metric_name,
            topic_name=topic_name,
        )
        time_series = [
            *FakeCoreTimeSeriesFactory.build_example_covid_time_series_range(),
            matching_record,
        ]
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=time_series
        )

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        metric_has_multiple_records: bool = (
            validator._does_metric_have_multiple_records()
        )

        # Then
        assert not metric_has_multiple_records

    def test_returns_false_for_non_existent_record(self):
        """
        Given a metric and a topic for a record which does not exist
        When `does_metric_have_multiple_records()` is called from an instance of `PlotValidation`
        Then False is returned
        """
        # Given
        plot_parameters = PlotParameters(
            metric="non_existent_metric_name",
            topic="non_existent_topic_name",
            chart_type=ChartTypes.simple_line.value,
            date_from="2022-01-01",
        )

        time_series = FakeCoreTimeSeriesFactory.build_example_covid_time_series_range()
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=time_series
        )

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        metric_has_multiple_records: bool = (
            validator._does_metric_have_multiple_records()
        )

        # Then
        assert not metric_has_multiple_records


class TestIsChartSeriesType:
    def test_waffle_chart_returns_false(self):
        """
        Given a chart type of `waffle`
        When `is_chart_series_type()` is called from an instance of `PlotValidation`
        Then False is returned
        """
        # Given
        chart_type = ChartTypes.waffle.value
        plot_parameters = PlotParameters(
            metric="covid_occupied_beds_latest",
            topic="COVID-19",
            chart_type=chart_type,
            date_from="2023-01-01",
        )

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When
        chart_is_series_type: bool = validator._is_chart_series_type()

        # Then
        assert not chart_is_series_type

    @pytest.mark.parametrize(
        "chart_type",
        [ChartTypes.simple_line.value, ChartTypes.line_with_shaded_section.value],
    )
    def test_line_charts_returns_true(self, chart_type: str):
        """
        Given a line/timeseries chart type
        When `is_chart_series_type()` is called from an instance of `PlotValidation`
        Then True is returned
        """
        # Given
        time_series_chart_type: str = chart_type
        plot_parameters = PlotParameters(
            metric="covid_occupied_beds_latest",
            topic="COVID-19",
            chart_type=time_series_chart_type,
            date_from="2023-01-01",
        )

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When
        chart_is_series_type: bool = validator._is_chart_series_type()

        # Then
        assert chart_is_series_type


class TestAreDatesInChronologicalOrder:
    def test_can_validate_successfully(self, valid_plot_parameters: PlotParameters):
        """
        Given a `date_from` and `date_to` which are in chronological order
        When `_are_dates_in_chronological_order()` is called
            from an instance of the `PlotValidation`
        Then True is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        date_from = datetime.datetime(year=2022, month=10, day=2)
        date_to = datetime.datetime(year=2023, month=2, day=3)
        plot_parameters.date_from = date_from.strftime(EXPECTED_DATE_FORMAT)
        plot_parameters.date_to = date_to.strftime(EXPECTED_DATE_FORMAT)

        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
        )

        # When
        is_date_stamps_in_chronological_order: bool = (
            validator._are_dates_in_chronological_order()
        )

        # Then
        assert is_date_stamps_in_chronological_order

    def test_raises_error_when_date_to_is_before_date_from(self):
        """
        Given a `date_from` and `date_to` which are not in chronological order
        When `_are_dates_in_chronological_order()` is called
            from an instance of the `ChartsRequestValidator`
        Then False is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        date_from = datetime.datetime(year=2022, month=10, day=1)
        date_to = datetime.datetime(year=2021, month=1, day=1)
        plot_parameters.date_from = date_from.strftime(EXPECTED_DATE_FORMAT)
        plot_parameters.date_to = date_to.strftime(EXPECTED_DATE_FORMAT)

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When / Then
        date_stamps_in_chronological_order: bool = (
            validator._are_dates_in_chronological_order()
        )

        # Then
        assert not date_stamps_in_chronological_order


class TestValidateDates:
    @mock.patch.object(validation.PlotValidation, "_are_dates_in_chronological_order")
    def test_delegates_call_for_checking_chronological_order(
        self,
        spy_are_dates_in_chronological_order: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given `date_from` and `date_to` stamps
        When `_validate_dates()` is called
            from an instance of the `PlotValidation`
        Then the call is delegated to the `_are_dates_in_chronological_order()` method
        """
        # Given
        plot_parameters = valid_plot_parameters
        date_from = datetime.datetime(year=2022, month=10, day=1)
        date_to = datetime.datetime(year=2023, month=12, day=2)
        plot_parameters.date_from = date_from.strftime(EXPECTED_DATE_FORMAT)
        plot_parameters.date_to = date_to.strftime(EXPECTED_DATE_FORMAT)

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When
        validated = validator._validate_dates()

        # Then
        assert validated is None
        spy_are_dates_in_chronological_order.assert_called_once()

    def test_chronological_order_validated_if_no_date_to_is_provided(self):
        """
        Given a valid `date_from` and None provided as `date_to`
        When `_validate_dates()` is called
            from an instance of the `PlotValidation`
        Then None is returned and no error is raised
        """
        # Given
        plot_parameters = valid_plot_parameters
        plot_parameters.date_from = "2022-01-01"
        plot_parameters.date_to = None

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When
        validated = validator._validate_dates()

        # Then
        assert validated is None

    def test_raises_error_if_not_in_chronological_order(self):
        """
        Given `date_from` and `date_to` stamps which are not in chronological order
        When `_validate_dates()` is called
            from an instance of the `PlotValidation`
        Then a `DatesNotInChronologicalOrderError` is raised
        """
        # Given
        date_from = datetime.datetime(year=2022, month=10, day=2)
        date_to = datetime.datetime(year=2021, month=7, day=1)
        plot_parameters = PlotParameters(
            metric="covid_occupied_beds_latest",
            topic="COVID-19",
            chart_type=ChartTypes.simple_line.value,
            date_from=date_from.strftime(EXPECTED_DATE_FORMAT),
            date_to=date_to.strftime(EXPECTED_DATE_FORMAT),
        )

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When / Then
        with pytest.raises(validation.DatesNotInChronologicalOrderError):
            validator._validate_dates()
