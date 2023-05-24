import datetime
from typing import List
from unittest import mock

import pytest

from metrics.domain.models import PlotParameters, PlotsCollection, PlotsData
from metrics.interfaces.plots.access import (
    DataNotFoundError,
    PlotsInterface,
    make_datetime_from_string,
)
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries

MODULE_PATH = "metrics.interfaces.plots.access"


class TestPlotsInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(plot_parameters: PlotParameters):
        return [
            FakeCoreTimeSeriesFactory.build_time_series(
                dt=datetime.date(year=2023, month=2, day=i + 1),
                metric_name=plot_parameters.metric_name,
                topic_name=plot_parameters.topic_name,
                stratum_name=plot_parameters.stratum_name,
            )
            for i in range(10)
        ]

    @mock.patch.object(PlotsInterface, "build_plot_data_from_parameters")
    def test_build_plots_data_delegates_call_for_each_plot(
        self,
        spy_build_plot_data_from_parameters: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
        fake_chart_plot_parameters_covid_cases: PlotParameters,
    ):
        """
        Given a `Plots` model which contains `PlotParameters` for 2 separate plots
        When `build_plots_data()` is called from an instance of the `PlotsInterface`
        Then the calls are delegated to the `build_plot_data_from_parameters()` method
            for each individual `PlotParameters` model
        """
        # Given
        fake_plots_collection = PlotsCollection(
            plots=[fake_chart_plot_parameters, fake_chart_plot_parameters_covid_cases],
            file_format="png",
            chart_width=123,
            chart_height=456,
        )

        data_slice_interface = PlotsInterface(
            plots_collection=fake_plots_collection,
            core_time_series_manager=mock.Mock(),
        )

        # When
        plots_data = data_slice_interface.build_plots_data()

        # Then
        # Check that `build_plot_data_from_parameters()` method
        # is called for each of the provided `PlotParameters` models
        expected_calls = [
            mock.call(plot_parameters=fake_chart_plot_parameters),
            mock.call(plot_parameters=fake_chart_plot_parameters_covid_cases),
        ]
        spy_build_plot_data_from_parameters.assert_has_calls(
            calls=expected_calls,
            any_order=False,
        )

        expected_plots_data = [spy_build_plot_data_from_parameters.return_value] * 2
        assert plots_data == expected_plots_data

    def test_build_plot_data_from_parameters(
        self, fake_chart_plot_parameters: PlotParameters
    ):
        """
        Given a `PlotParameters` model requesting a plot for existing `CoreTimeSeries`
        When `build_plot_data_from_parameters()` is called from an instance of the `PlotsInterface`
        Then a `PlotData` model is returned with the original parameters
        And the correct data passed to the `x_axis` and `y_axis`
        """
        # Given
        fake_plots_collection = PlotsCollection(
            plots=[fake_chart_plot_parameters],
            file_format="png",
            chart_width=123,
            chart_height=456,
        )
        fake_core_time_series_for_plot: List[
            FakeCoreTimeSeries
        ] = self._setup_fake_time_series_for_plot(
            plot_parameters=fake_chart_plot_parameters
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_for_plot
        )

        plots_interface = PlotsInterface(
            plots_collection=fake_plots_collection,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        plot_data: PlotsData = plots_interface.build_plot_data_from_parameters(
            plot_parameters=fake_chart_plot_parameters
        )

        # Then
        # Check that the parameters on the `PlotData` model is ingested by the input `PlotParameters` model
        assert plot_data.parameters == fake_chart_plot_parameters

        # Check the correct data is passed to the axis of the `PlotData` model
        assert plot_data.x_axis == tuple(x.dt for x in fake_core_time_series_for_plot)
        assert plot_data.y_axis == tuple(
            x.metric_value for x in fake_core_time_series_for_plot
        )

    def test_build_plot_data_from_parameters_raises_error_when_no_data_found(
        self, fake_chart_plot_parameters: PlotParameters
    ):
        """
        Given a `PlotParameters` model requesting a plot for `CoreTimeSeries` data which cannot be found
        When `build_plot_data_from_parameters()` is called from an instance of the `PlotsInterface`
        Then a `DataNotFoundError` is raised
        """
        # Given
        fake_plots_collection = PlotsCollection(
            plots=[fake_chart_plot_parameters],
            file_format="png",
            chart_width=123,
            chart_height=456,
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])

        plots_interface = PlotsInterface(
            plots_collection=fake_plots_collection,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundError):
            plots_interface.build_plot_data_from_parameters(
                plot_parameters=fake_chart_plot_parameters
            )

    def test_get_timeseries_calls_core_time_series_manager_with_correct_args(self):
        """
        Given a `CoreTimeSeriesManager`
        When `get_timeseries()` is called from an instance of `PlotsInterface`
        Then the correct method is called from `CoreTimeSeriesManager` to retrieve the timeseries
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        mocked_date_from = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()

        plots_interface = PlotsInterface(
            plots_collection=mock.MagicMock(),
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        timeseries = plots_interface.get_timeseries(
            topic_name=mocked_topic,
            metric_name=mocked_metric,
            date_from=mocked_date_from,
            geography_name=mocked_geography,
            geography_type_name=mocked_geography_type,
            stratum_name=mocked_stratum,
        )

        # Then
        assert (
            timeseries
            == spy_core_time_series_manager.filter_for_dates_and_values.return_value
        )
        spy_core_time_series_manager.filter_for_dates_and_values.assert_called_once_with(
            topic_name=mocked_topic,
            metric_name=mocked_metric,
            date_from=mocked_date_from,
            geography_name=mocked_geography,
            geography_type_name=mocked_geography_type,
            stratum_name=mocked_stratum,
        )

    @mock.patch.object(PlotsInterface, "get_timeseries")
    def test_get_timeseries_for_plot_parameters_delegates_call_with_correct_args(
        self,
        mocked_get_timeseries: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model with a defined `date_from`
        When `get_timeseries_for_plot_parameters()` is called from an instance of the `PlotsInterface`
        Then the call is delegated to the `get_timeseries()` method with the correct args
        """
        # Given
        date_from: str = "2023-01-01"
        fake_chart_plot_parameters.date_from = date_from

        plots_interface = PlotsInterface(
            plots_collection=mock.MagicMock(), core_time_series_manager=mock.Mock()
        )

        # When
        timeseries = plots_interface.get_timeseries_for_plot_parameters(
            plot_parameters=fake_chart_plot_parameters
        )

        # Then
        # The return value is delegated to the `get_timeseries` method
        assert timeseries == mocked_get_timeseries.return_value

        # The dict representation of the `PlotParameters` model
        # is unpacked into the `get_timeseries` method
        mocked_get_timeseries.assert_called_once_with(
            **fake_chart_plot_parameters.to_dict_for_query(),
        )


class TestMakeDatetimeFromString:
    def test_returns_correct_value(self):
        """
        Given a valid date string in the format `%Y-%m-%d`
        When `make_datetime_from_string()` is called
        Then a `datetime.datetime` object is returned for the given date
        """
        # Given
        year = "2023"
        month = "01"
        day = "01"
        date_from = f"{year}-{month}-{day}"

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        assert type(parsed_date_from) == datetime.datetime
        assert parsed_date_from.year == int(year)
        assert parsed_date_from.month == int(month)
        assert parsed_date_from.day == int(day)

    @mock.patch(f"{MODULE_PATH}.get_date_n_months_ago_from_timestamp")
    def test_delegates_call_to_get_default_of_one_year_if_none_provided(
        self,
        spy_get_date_n_months_ago_from_timestamp: mock.MagicMock,
    ):
        """
        Given an input `date_from` of None
        When `make_datetime_from_string()` is called
        Then `get_date_n_months_ago_from_timestamp()` is called to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = None

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value

    @mock.patch(f"{MODULE_PATH}.get_date_n_months_ago_from_timestamp")
    def test_delegates_call_to_get_default_of_one_year_if_empty_string_provided(
        self,
        spy_get_date_n_months_ago_from_timestamp: mock.MagicMock,
    ):
        """
        Given an input `date_from` of an empty string
        When `make_datetime_from_string()` is called
        Then `get_date_n_months_ago_from_timestamp()` is called to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = ""

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value
