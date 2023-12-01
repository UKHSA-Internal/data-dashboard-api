import datetime
from unittest import mock

import pytest

from metrics.data.managers.core_models.metric import MetricManager
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


class TestValidate:
    @mock.patch.object(validation.PlotValidation, "_validate_dates")
    @mock.patch.object(
        validation.PlotValidation, "_validate_metric_is_available_for_topic"
    )
    def test_delegates_to_correct_validators(
        self,
        spy_validate_metric_is_available_for_topic: mock.MagicMock,
        spy_validate_dates: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given an instance of the `PlotValidation` class
        When `validate()` is called
        Then the correct sub validate methods are called and delegated to
        """
        # Given
        validator = validation.PlotValidation(
            plot_parameters=fake_chart_plot_parameters,
            core_time_series_manager=mock.Mock(),
            metric_manager=mock.Mock(),
        )

        # When
        validator.validate()

        # Then
        spy_validate_metric_is_available_for_topic.assert_called_once()
        spy_validate_dates.assert_called_once()


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
            chart_type=ChartTypes.simple_line.value,
            date_from=date_from.strftime(EXPECTED_DATE_FORMAT),
            date_to=date_to.strftime(EXPECTED_DATE_FORMAT),
        )

        validator = validation.PlotValidation(plot_parameters=plot_parameters)

        # When / Then
        with pytest.raises(validation.DatesNotInChronologicalOrderError):
            validator._validate_dates()
