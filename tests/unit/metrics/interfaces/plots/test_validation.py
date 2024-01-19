import datetime
from unittest import mock

import pytest

from metrics.domain.models import PlotParameters
from metrics.domain.utils import ChartTypes
from metrics.interfaces.plots import validation
from metrics.interfaces.plots.validation import (
    MetricDoesNotSupportTopicError,
    PlotValidation,
)

EXPECTED_DATE_FORMAT: str = "%Y-%m-%d"


class TestValidate:
    @mock.patch.object(validation.PlotValidation, "_validate_metric_with_topic")
    @mock.patch.object(validation.PlotValidation, "_validate_dates")
    def test_delegates_to_correct_validators(
        self,
        spy_validate_dates: mock.MagicMock,
        spy_validate_metric_with_topic: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given an instance of the `PlotValidation` class
        When `validate()` is called
        Then the correct sub validate methods are called and delegated to
        """
        # Given
        validator = validation.PlotValidation(
            plot_parameters=fake_chart_plot_parameters
        )

        # When
        validator.validate()

        # Then
        spy_validate_dates.assert_called_once()
        spy_validate_metric_with_topic.assert_called_once()


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

    def test_raises_error_when_date_to_is_before_date_from(
        self, valid_plot_parameters: PlotParameters
    ):
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

    def test_chronological_order_validated_if_no_date_to_is_provided(
        self, valid_plot_parameters: PlotParameters
    ):
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
            metric="COVID-19_deaths_ONSByDay",
            topic="COVID-19",
            chart_type=ChartTypes.line_multi_coloured.value,
            date_from=date_from.strftime(EXPECTED_DATE_FORMAT),
            date_to=date_to.strftime(EXPECTED_DATE_FORMAT),
        )

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When / Then
        with pytest.raises(validation.DatesNotInChronologicalOrderError):
            validator._validate_dates()


class TestValidateMetricWithTopic:
    @mock.patch.object(PlotValidation, "_metric_is_compatible_with_topic")
    def test_returns_none_when_metric_is_compatible_with_topic(
        self,
        mocked_metric_is_compatible_with_topic: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given the `_metric_is_compatible_with_topic()` method
            return True
        When `_validate_metric_with_topic()` is called
            from an instance of `PlotValidation`
        Then None is returned
        """
        # Given
        mocked_metric_is_compatible_with_topic.return_value = True
        validator = validation.PlotValidation(
            plot_parameters=fake_chart_plot_parameters
        )

        # When
        validated = validator._validate_metric_with_topic()

        # Then
        assert validated is None

    @mock.patch.object(PlotValidation, "_metric_is_compatible_with_topic")
    def test_raises_error_when_metric_is_not_compatible_with_topic(
        self,
        mocked_metric_is_compatible_with_topic: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given the `_metric_is_compatible_with_topic()` method
            return False
        When `_validate_metric_with_topic()` is called
            from an instance of `PlotValidation`
        Then a `MetricDoesNotSupportTopicError` is raised
        """
        # Given
        mocked_metric_is_compatible_with_topic.return_value = False
        validator = validation.PlotValidation(
            plot_parameters=fake_chart_plot_parameters
        )

        # When / Then
        with pytest.raises(MetricDoesNotSupportTopicError):
            validator._validate_metric_with_topic()


class TestMetricIsCompatibleWithTopic:
    @pytest.mark.parametrize(
        "metric, topic",
        (
            ("COVID-19_deaths_ONSByDay", "COVID-19"),
            ("influenza_headline_positivityLatest", "Influenza"),
            ("RSV_headline_positivityLatest", "RSV"),
            ("parainfluenza_testing_positivityByWeek", "Parainfluenza"),
            ("rhinovirus_headline_positivityLatest", "Rhinovirus"),
            ("hMPV_testing_positivityByWeek", "hMPV"),
            ("adenovirus_headline_positivityLatest", "Adenovirus"),
        ),
    )
    def test_returns_true_for_valid_metric_and_topic(
        self, metric: str, topic: str, valid_plot_parameters: PlotParameters
    ):
        """
        Given a `topic` and `metric` which are valid together
        When `_metric_is_compatible_with_topic()` is called
            from an instance of the `PlotValidation`
        Then True is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        plot_parameters.metric = metric
        plot_parameters.topic = topic
        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
        )

        # When
        is_metric_valid_with_topic: bool = validator._metric_is_compatible_with_topic()

        # Then
        assert is_metric_valid_with_topic

    @pytest.mark.parametrize(
        "metric, topic",
        (
            ("COVID-19_deaths_ONSByDay", "Adenovirus"),
            ("influenza_headline_positivityLatest", "hMPV"),
            ("RSV_headline_positivityLatest", "Rhinovirus"),
            ("parainfluenza_testing_positivityByWeek", "RSV"),
            ("rhinovirus_headline_positivityLatest", "Parainfluenza"),
            ("hMPV_testing_positivityByWeek", "Influenza"),
            ("adenovirus_headline_positivityLatest", "COVID-19"),
        ),
    )
    def test_returns_false_for_invalid_metric_and_topic(
        self, metric: str, topic: str, valid_plot_parameters: PlotParameters
    ):
        """
        Given a `topic` and `metric` which are not valid together
        When `_metric_is_compatible_with_topic()` is called
            from an instance of the `PlotValidation`
        Then False is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        plot_parameters.metric = metric
        plot_parameters.topic = topic
        validator = validation.PlotValidation(
            plot_parameters=plot_parameters,
        )

        # When
        is_metric_valid_with_topic: bool = validator._metric_is_compatible_with_topic()

        # Then
        assert not is_metric_valid_with_topic
