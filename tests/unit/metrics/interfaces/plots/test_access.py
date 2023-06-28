import datetime
from typing import List, Union
from unittest import mock

import pytest

from metrics.domain.models import PlotParameters, PlotsCollection, PlotsData
from metrics.domain.utils import ChartAxisFields
from metrics.interfaces.plots.access import (
    DataNotFoundError,
    PlotsInterface,
    convert_type,
    create_sort,
    get_x_and_y_values,
    sort_by_stratum,
    unzip_values,
)
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries

MODULE_PATH = "metrics.interfaces.plots.access"


class TestPlotsInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(
        plot_parameters: PlotParameters,
    ) -> List[FakeCoreTimeSeries]:
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

    def test_build_plots_data_passes_for_plot_parameters_with_no_supporting_data(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given a request for a plot with no supporting data and another which has supporting data
        When `build_plots_data()` is called from an instance of the `PlotsInterface`
        Then only 1 enriched `PlotData` model is returned
            for the `PlotParameters` which requested timeseries data that existed
        """
        # Given
        plot_parameters_with_no_supporting_data = PlotParameters(
            metric="non_existent_metric",
            topic="non_existent_topic",
            chart_type="line",
        )
        plots_collection = PlotsCollection(
            plots=[valid_plot_parameters, plot_parameters_with_no_supporting_data],
            file_format="svg",
            chart_width=123,
            chart_height=456,
        )
        fake_core_time_series_records: List[
            FakeCoreTimeSeries
        ] = self._setup_fake_time_series_for_plot(plot_parameters=valid_plot_parameters)
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_records
        )

        plots_interface = PlotsInterface(
            plots_collection=plots_collection,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        plots_data: List[PlotsData] = plots_interface.build_plots_data()

        # Then
        # Check that only 1 enriched `PlotData` model is returned
        assert len(plots_data) == 1

        # Check that the `PlotData` model was enriched
        # for the plot parameters which requested timeseries data that existed
        expected_plots_data_for_valid_params = PlotsData(
            parameters=valid_plot_parameters,
            x_axis_values=tuple(x.dt for x in fake_core_time_series_records),
            y_axis_values=tuple(x.metric_value for x in fake_core_time_series_records),
        )
        assert plots_data == [expected_plots_data_for_valid_params]

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
        assert plot_data.x_axis_values == tuple(
            x.dt for x in fake_core_time_series_for_plot
        )
        assert plot_data.y_axis_values == tuple(
            x.metric_value for x in fake_core_time_series_for_plot
        )

    @mock.patch.object(PlotsInterface, "get_timeseries_for_plot_parameters")
    @mock.patch(f"{MODULE_PATH}.get_x_and_y_values")
    def test_build_plot_data_from_parameters_calls_get_x_and_y_values(
        self,
        spy_get_x_and_y_values: mock.MagicMock,
        mocked_get_timeseries_for_plot_parameters: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a set of `ChartParameters` and fake X and Y axis values
        When `build_plot_data_from_parameters()` is called from an instance of `PlotsInterface`
        Then the call is delegated to `get_x_and_y_values()` to fetch the values
        And those values are set on the `x_axis` and `y_axis` on returned model
        """
        # Given
        fake_x_axis_values = [1, 2, 3]
        fake_y_axis_values = ["a", "b", "c"]
        spy_get_x_and_y_values.return_value = fake_x_axis_values, fake_y_axis_values
        plots_interface = PlotsInterface(
            plots_collection=mock.Mock(),
            core_time_series_manager=mock.Mock(),
        )

        # When
        plot_data_from_parameters: PlotsData = (
            plots_interface.build_plot_data_from_parameters(
                plot_parameters=fake_chart_plot_parameters
            )
        )

        # Then
        spy_get_x_and_y_values.assert_called_once_with(
            plot_parameters=fake_chart_plot_parameters,
            queryset=mocked_get_timeseries_for_plot_parameters.return_value,
        )

        # Check that the enriched `PlotsData` model has been set
        # with the correct values via the `get_x_any_y_values` function
        assert plot_data_from_parameters.x_axis_values == fake_x_axis_values
        assert plot_data_from_parameters.y_axis_values == fake_y_axis_values

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
        mocked_x_axis = mock.Mock()
        mocked_y_axis = mock.Mock()
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        mocked_date_from = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()
        mocked_sex = mock.Mock()

        plots_interface = PlotsInterface(
            plots_collection=mock.MagicMock(),
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        timeseries = plots_interface.get_timeseries(
            x_axis=mocked_x_axis,
            y_axis=mocked_y_axis,
            topic_name=mocked_topic,
            metric_name=mocked_metric,
            date_from=mocked_date_from,
            geography_name=mocked_geography,
            geography_type_name=mocked_geography_type,
            stratum_name=mocked_stratum,
            sex=mocked_sex,
        )

        # Then
        assert (
            timeseries
            == spy_core_time_series_manager.filter_for_x_and_y_values.return_value
        )
        spy_core_time_series_manager.filter_for_x_and_y_values.assert_called_once_with(
            x_axis=mocked_x_axis,
            y_axis=mocked_y_axis,
            topic_name=mocked_topic,
            metric_name=mocked_metric,
            date_from=mocked_date_from,
            geography_name=mocked_geography,
            geography_type_name=mocked_geography_type,
            stratum_name=mocked_stratum,
            sex=mocked_sex,
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
        fake_plots_collection = mock.MagicMock()

        plots_interface = PlotsInterface(
            plots_collection=fake_plots_collection, core_time_series_manager=mock.Mock()
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


class TestGetXAndYValues:
    @mock.patch(f"{MODULE_PATH}.sort_by_stratum")
    def test_can_delegate_call_to_sort_by_stratum(
        self,
        spy_sort_by_stratum: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model which requests `stratum` along the X-axis
        When `get_x_and_y_values()` is called
        Then the call is delegated to `sort_by_stratum()`
        """
        # Given
        fake_chart_plot_parameters.x_axis = ChartAxisFields.stratum.name
        mocked_queryset = mock.Mock()

        # When
        x_and_y_values = get_x_and_y_values(
            plot_parameters=fake_chart_plot_parameters, queryset=mocked_queryset
        )

        # Then
        assert x_and_y_values == spy_sort_by_stratum.return_value
        spy_sort_by_stratum.assert_called_once_with(queryset=mocked_queryset)

    @pytest.mark.parametrize(
        "x_axis",
        [
            ChartAxisFields.date.name,
            ChartAxisFields.metric.name,
            ChartAxisFields.geography.name,
        ],
    )
    @mock.patch(f"{MODULE_PATH}.unzip_values")
    def test_delegates_call_to_unzip_values(
        self,
        spy_unzip_values: mock.MagicMock,
        x_axis: str,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model which does not request `stratum` along the X-axis
        When `get_x_and_y_values()` is called
        Then the call is delegated to `unzip_values()`
        """
        # Given
        mocked_queryset = mock.Mock()
        fake_chart_plot_parameters.x_axis = x_axis

        # When
        x_and_y_values = get_x_and_y_values(
            plot_parameters=fake_chart_plot_parameters, queryset=mocked_queryset
        )

        # Then
        assert x_and_y_values == spy_unzip_values.return_value
        spy_unzip_values.assert_called_once_with(values=mocked_queryset)


class TestConvertType:
    @pytest.mark.parametrize(
        "mock_input, mock_output",
        [
            ("85", 85),
            ("04", 4),
            ("default", "default"),
        ],
    )
    def test_basic_operation(self, mock_input: str, mock_output: Union[int, str]):
        """
        Given a string that may or may not contain a number
        When `convert_type()` is called
        Then expected result is returned
        """
        # Given/When
        actual_output = convert_type(s=mock_input)

        # Then
        assert mock_output == actual_output


class TestCreateSort:
    @pytest.mark.parametrize(
        "mock_input, mock_output",
        [
            ("0_4", (0, 4)),
            ("20_24", (20, 24)),
            ("65+", (65,)),
            ("default", (999, 999, "default")),
        ],
    )
    def test_basic_operation(self, mock_input: str, mock_output: Union[int, str]):
        """
        Given a string that may or may not contain numbers
        When `create_sort()` is called
        Then expected result is returned
        """
        # Given/When
        actual_output = create_sort(stratum=mock_input)

        # Then
        assert mock_output == actual_output


class TestSortByStratum:
    def test_returns_correct_x_and_y_values(self):
        """
        Given a list of 4 * 2-item tuples
        When `sort_by_stratum()` is called
        Then the result is 2 tuples which contain 4 items each
        And sorted properly
        And in display format
        """
        # Given
        values = [("default", 5), ("65_84", 1), ("6_17", 2), ("85+", 3), ("18_64", 4)]

        # When
        first_list, second_list = sort_by_stratum(values)

        # Then
        assert first_list == ["6-17", "18-64", "65-84", "85+", "default"]
        assert second_list == [2, 4, 1, 3, 5]


class TestUnzipValues:
    def test_returns_correct_zipped_values(self):
        """
        Given a list of 3 * 2-item tuples
        When `unzip_values()` is called
        Then the result is 2 tuples which contain 3 items each
        """
        # Given
        values = [(1, 2), (3, 4), (5, 6)]

        # When
        unzipped_lists = unzip_values(values)

        # Then
        (
            first_index_item_unzipped_result,
            second_index_item_unzipped_result,
        ) = unzipped_lists

        assert first_index_item_unzipped_result == (1, 3, 5)
        assert second_index_item_unzipped_result == (2, 4, 6)
