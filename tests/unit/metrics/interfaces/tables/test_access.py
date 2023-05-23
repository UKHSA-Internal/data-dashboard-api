import datetime
from typing import List
from unittest import mock

import pytest

from metrics.domain.models import TablePlotParameters, TablePlots, TabularPlotData
from metrics.interfaces.tables.access import (
    DataNotFoundError,
    TablesInterface,
    generate_tabular_output,
    make_datetime_from_string,
    validate_each_requested_table_plot,
    validate_table_plot_parameters,
)
from metrics.interfaces.tables.validation import TablesRequestValidator
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries

MODULE_PATH = "metrics.interfaces.tables.access"


class TestTablesInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(table_plot_parameters: TablePlotParameters):
        return [
            FakeCoreTimeSeriesFactory.build_time_series(
                dt=datetime.datetime(year=2023, month=1, day=i + 1),
                metric_name=table_plot_parameters.metric,
                topic_name=table_plot_parameters.topic,
                stratum_name=table_plot_parameters.stratum,
            )
            for i in range(10)
        ]

    def test_build_table_plot_data_from_parameters(
        self, fake_table_plot_parameters: TablePlotParameters
    ):
        """
        Given a `TablePlotParameters` model requesting a table plot for existing `CoreTimeSeries`
        When `build_table_plot_data_from_parameters()` is called from an instance of the `TablesInterface`
        Then a `TabularPlotData` model is returned with the original parameters
        And the correct data passed to the `x_axis` and `y_axis`
        """
        # Given
        fake_table_plots = TablePlots(
            plots=[fake_table_plot_parameters],
        )
        fake_core_time_series_for_plot: List[
            FakeCoreTimeSeries
        ] = self._setup_fake_time_series_for_plot(
            table_plot_parameters=fake_table_plot_parameters
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_for_plot
        )

        tables_interface = TablesInterface(
            table_plots=fake_table_plots,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        table_plot_data: TabularPlotData = (
            tables_interface.build_table_plot_data_from_parameters(
                table_plot_parameters=fake_table_plot_parameters
            )
        )

        # Then
        # Check that the parameters on the `TabularPlotData` model is ingested by the input `TablePlotParameters` model
        assert table_plot_data.parameters == fake_table_plot_parameters

        # Check the correct data is passed to the axis of the `TabularPlotData` model
        assert table_plot_data.x_axis_values == tuple(
            x.dt for x in fake_core_time_series_for_plot
        )
        assert table_plot_data.y_axis_values == tuple(
            x.metric_value for x in fake_core_time_series_for_plot
        )

    def test_build_table_plot_data_from_parameters_raises_error_when_no_data_found(
        self, fake_table_plot_parameters: TablePlotParameters
    ):
        """
        Given a `TablePlotParameters` model requesting a table plot for `CoreTimeSeries` data which cannot be found
        When `build_table_plot_data_from_parameters()` is called from an instance of the `TablesInterface`
        Then a `DataNotFoundError` is raised
        """
        # Given
        fake_table_plots = TablePlots(
            plots=[fake_table_plot_parameters],
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])

        tables_interface = TablesInterface(
            table_plots=fake_table_plots,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundError):
            tables_interface.build_table_plot_data_from_parameters(
                table_plot_parameters=fake_table_plot_parameters
            )

    def test_get_timeseries_calls_core_time_series_manager_with_correct_args(self):
        """
        Given a `CoreTimeSeriesManager`
        When `get_timeseries()` is called from an instance of `TablesInterface`
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

        tables_interface = TablesInterface(
            table_plots=mock.MagicMock(),
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        timeseries = tables_interface.get_timeseries(
            topic=mocked_topic,
            metric=mocked_metric,
            date_from=mocked_date_from,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            stratum=mocked_stratum,
        )

        # Then
        assert (
            timeseries
            == spy_core_time_series_manager.filter_for_dates_and_values.return_value
        )
        spy_core_time_series_manager.filter_for_dates_and_values.assert_called_once_with(
            topic=mocked_topic,
            metric=mocked_metric,
            date_from=mocked_date_from,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            stratum=mocked_stratum,
        )

    @mock.patch.object(TablesInterface, "get_timeseries")
    def test_get_timeseries_for_table_plot_parameters_delegates_call_with_correct_args(
        self,
        mocked_get_timeseries: mock.MagicMock,
        fake_table_plot_parameters: TablePlotParameters,
    ):
        """
        Given a `TablePlotParameters` model with a defined `date_from`
        When `get_timeseries_for_table_plot_parameters()` is called from an instance of the `TablesInterface`
        Then the call is delegated to the `get_timeseries()` method with the correct args
        """
        # Given
        date_from: str = "2023-01-01"
        fake_table_plot_parameters.date_from = date_from

        tables_interface = TablesInterface(
            table_plots=mock.MagicMock(), core_time_series_manager=mock.Mock()
        )

        # When
        timeseries = tables_interface.get_timeseries_for_table_plot_parameters(
            table_plot_parameters=fake_table_plot_parameters
        )

        # Then
        # The return value is delegated to the `get_timeseries` method
        assert timeseries == mocked_get_timeseries.return_value

        expected_date_from = make_datetime_from_string(date_from=date_from)
        # The dict representation of the `TablePlotParameters` model
        # is unpacked into the `get_timeseries` method
        mocked_get_timeseries.assert_called_once_with(
            **fake_table_plot_parameters.to_dict_for_query(),
            date_from=expected_date_from,
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


class TestValidateEachRequestedTablePlot:
    @mock.patch(f"{MODULE_PATH}.validate_table_plot_parameters")
    def test_delegates_call_for_each_table_plot(
        self,
        spy_validate_table_plot_parameters: mock.MagicMock,
        fake_table_plot_parameters: TablePlotParameters,
        fake_table_plot_parameters_covid_cases: TablePlotParameters,
    ):
        """
        Given a `TablePlots` model requesting plots
            of multiple `TablePlotParameters` models
        When `validate_each_requested_table_plot()` is called
        Then the call is delegated to `validate_table_plot_parameters()`
            for each `TablePlotParameters` models
        """
        # Given
        fake_requested_table_plots = [
            fake_table_plot_parameters,
            fake_table_plot_parameters_covid_cases,
        ]
        fake_table_plots = TablePlots(
            plots=fake_requested_table_plots,
        )

        # When
        validate_each_requested_table_plot(table_plots=fake_table_plots)

        # Then
        expected_calls = [
            mock.call(table_plot_parameters=requested_table_plot)
            for requested_table_plot in fake_requested_table_plots
        ]
        spy_validate_table_plot_parameters.assert_has_calls(calls=expected_calls)


class TestValidateTablePlotParameters:
    @mock.patch.object(TablesRequestValidator, "validate")
    def test_delegates_call_to_validate_method_on_table_request_validator_class(
        self,
        spy_validate_method: mock.MagicMock,
        fake_table_plot_parameters: TablePlotParameters,
    ):
        """
        Given a `TablePlotParameters` model
        When `validate_table_plot_parameters()` is called
        Then the call is delegated to the `validate()` from an instance of the `TableRequestValidator`
        """
        # Given
        table_plot_parameters = fake_table_plot_parameters

        # When
        validate_table_plot_parameters(table_plot_parameters=table_plot_parameters)

        # Then
        spy_validate_method.assert_called_once()
