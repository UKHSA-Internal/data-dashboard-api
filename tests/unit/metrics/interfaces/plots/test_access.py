import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.domain.models import (
    PlotGenerationData,
    PlotParameters,
    ChartRequestParams,
)
from metrics.domain.models.plots import CompletePlotData
from metrics.domain.common.utils import ChartAxisFields
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    DataNotFoundForPlotError,
    InvalidPlotParametersError,
    PlotsInterface,
    QuerySetResult,
    _build_age_display_name,
    convert_type,
    get_aggregated_results,
    aggregate_results_by_age,
)
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.managers.topic_manager import FakeTopicManager
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries
from tests.fakes.models.queryset import FakeQuerySet

MODULE_PATH = "metrics.interfaces.plots.access"


class TestPlotsInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(
        plot_parameters: PlotParameters,
    ) -> list[FakeCoreTimeSeries]:
        return [
            FakeCoreTimeSeriesFactory.build_time_series(
                date=datetime.date(year=2023, month=2, day=i + 1),
                metric=plot_parameters.metric,
                topic=plot_parameters.topic,
                stratum=plot_parameters.stratum,
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
        fake_chart_request_params = ChartRequestParams(
            plots=[fake_chart_plot_parameters, fake_chart_plot_parameters_covid_cases],
            file_format="png",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )

        data_slice_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=mock.Mock(),
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
            metric="non_cases_topic_cases_abc",
            topic="non_cases_topic",
            chart_type="line",
            date_from="2023-01-01",
            date_to="2023-12-31",
        )
        chart_request_params = ChartRequestParams(
            plots=[valid_plot_parameters, plot_parameters_with_no_supporting_data],
            file_format="svg",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )
        fake_core_time_series_records: list[FakeCoreTimeSeries] = (
            self._setup_fake_time_series_for_plot(plot_parameters=valid_plot_parameters)
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_records
        )

        plots_interface = PlotsInterface(
            chart_request_params=chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When
        plots_data: list[PlotGenerationData] = plots_interface.build_plots_data()

        # Then
        # Check that only 1 enriched `PlotData` model is returned
        assert len(plots_data) == 1

        # Check that the `PlotData` model was enriched
        # for the plot parameters which requested timeseries data that existed
        expected_plots_data_for_valid_params = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values=[x.date for x in fake_core_time_series_records],
            y_axis_values=[x.metric_value for x in fake_core_time_series_records],
            additional_values={
                "in_reporting_delay_period": [
                    x.in_reporting_delay_period for x in fake_core_time_series_records
                ]
            },
            latest_date=str(max(x.date for x in fake_core_time_series_records)),
        )
        assert plots_data == [expected_plots_data_for_valid_params]

    def test_build_plots_data_raises_error_when_all_plots_return_no_data(
        self, fake_chart_request_params: ChartRequestParams
    ):
        """
        Given a request with a `PlotsCollection` model
            which will return no data for any of its plots
        When `build_plots_data()` is called from
            an instance of the `PlotsInterface`
        Then a `DataNotFoundForAnyPlotError` is raised
        """
        # Given
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])
        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundForAnyPlotError):
            plots_interface.build_plots_data()

    @mock.patch.object(
        PlotsInterface, "build_plot_data_from_parameters_with_complete_queryset"
    )
    def test_build_plots_data_for_full_queryset_delegates_call_for_each_plot(
        self,
        spy_build_plot_data_from_parameters_with_complete_queryset: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
        fake_chart_plot_parameters_covid_cases: PlotParameters,
    ):
        """
        Given a `PlotsCollection` model which
            contains `PlotParameters` for 2 separate plots
        When `build_plots_data_for_full_queryset()` is called
            from an instance of the `PlotsInterface`
        Then the calls are delegated to the
            `build_plot_data_from_parameters_with_complete_queryset()` method
            for each individual `PlotParameters` model
        """
        # Given
        fake_chart_request_params = ChartRequestParams(
            plots=[fake_chart_plot_parameters, fake_chart_plot_parameters_covid_cases],
            file_format="png",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )

        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=mock.Mock(),
        )

        # When
        plots_data = plots_interface.build_plots_data_for_full_queryset()

        # Then
        # Check that `build_plot_data_from_parameters_with_complete_queryset()` method
        # is called for each of the provided `PlotParameters` models
        expected_calls = [
            mock.call(plot_parameters=fake_chart_plot_parameters),
            mock.call(plot_parameters=fake_chart_plot_parameters_covid_cases),
        ]
        spy_build_plot_data_from_parameters_with_complete_queryset.assert_has_calls(
            calls=expected_calls,
            any_order=False,
        )

        expected_plots_data = [
            spy_build_plot_data_from_parameters_with_complete_queryset.return_value
        ] * 2
        assert plots_data == expected_plots_data

    def test_build_plots_data_for_full_queryset_passes_for_plot_parameters_with_no_supporting_data(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given a request for a plot with no supporting data
        And another which has supporting data
        When `build_plot_data_from_parameters_with_complete_queryset()`
            is called from an instance of the `PlotsInterface`
        Then only 1 enriched `PlotData` model is returned
            for the `PlotParameters` which requested timeseries data that existed
        """
        # Given
        plot_parameters_with_no_supporting_data = PlotParameters(
            metric="non_cases_topic_cases_abc",
            topic="non_cases_topic",
            chart_type="line",
            date_from="2023-01-01",
            date_to="2023-12-31",
        )
        fake_chart_request_params = ChartRequestParams(
            plots=[valid_plot_parameters, plot_parameters_with_no_supporting_data],
            file_format="svg",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )
        fake_core_time_series_records: list[FakeCoreTimeSeries] = (
            self._setup_fake_time_series_for_plot(plot_parameters=valid_plot_parameters)
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_records
        )

        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When
        plots_data: list[CompletePlotData] = (
            plots_interface.build_plots_data_for_full_queryset()
        )

        # Then
        # Check that only 1 enriched `CompletePlotData` model is returned
        assert len(plots_data) == 1

        # Check that the `CompletePlotData` model was enriched
        # for the plot parameters which requested timeseries data that existed
        assert plots_data[0].parameters == valid_plot_parameters

    def test_build_plots_data_for_full_queryset_raises_error_when_all_plots_return_no_data(
        self, fake_chart_request_params: ChartRequestParams
    ):
        """
        Given a request with a `PlotsCollection` model
            which will return no data for any of its plots
        When `build_plots_data_for_full_queryset()` is called
            from an instance of the `PlotsInterface`
        Then a `DataNotFoundForAnyPlotError` is raised
        """
        # Given
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])
        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundForAnyPlotError):
            plots_interface.build_plots_data_for_full_queryset()

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
        fake_chart_request_params = ChartRequestParams(
            plots=[fake_chart_plot_parameters],
            file_format="png",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )
        fake_core_time_series_for_plot: list[FakeCoreTimeSeries] = (
            self._setup_fake_time_series_for_plot(
                plot_parameters=fake_chart_plot_parameters
            )
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_for_plot
        )

        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When
        plot_data: PlotGenerationData = plots_interface.build_plot_data_from_parameters(
            plot_parameters=fake_chart_plot_parameters
        )

        # Then
        # Check that the parameters on the `PlotData` model is ingested by the input `PlotParameters` model
        assert plot_data.parameters == fake_chart_plot_parameters

        # Check the correct data is passed to the axis of the `PlotData` model
        assert plot_data.x_axis_values == [
            x.date for x in fake_core_time_series_for_plot
        ]
        assert plot_data.y_axis_values == [
            x.metric_value for x in fake_core_time_series_for_plot
        ]

    @mock.patch.object(PlotsInterface, "get_queryset_result_for_plot_parameters")
    @mock.patch(f"{MODULE_PATH}.get_aggregated_results")
    def test_build_plot_data_from_parameters_calls_get_aggregated_results(
        self,
        spy_get_aggregated_results: mock.MagicMock,
        mocked_get_queryset_result_for_plot_parameters: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a set of `ChartParameters` and fake X and Y axis values
        When `build_plot_data_from_parameters()` is called from an instance of `PlotsInterface`
        Then the call is delegated to `get_aggregated_results()` to fetch the values
        And those values are set on the `x_axis` and `y_axis` on returned model
        """
        # Given
        fake_x_axis_values = [1, 2, 3]
        fake_y_axis_values = ["a", "b", "c"]
        spy_get_aggregated_results.return_value = {
            "date": fake_x_axis_values,
            "metric_value": fake_y_axis_values,
        }
        plots_interface = PlotsInterface(
            chart_request_params=mock.Mock(plots=[]),
            core_model_manager=mock.Mock(),
        )

        # When
        plot_data_from_parameters: PlotGenerationData = (
            plots_interface.build_plot_data_from_parameters(
                plot_parameters=fake_chart_plot_parameters
            )
        )

        # Then
        spy_get_aggregated_results.assert_called_once_with(
            plot_parameters=fake_chart_plot_parameters,
            queryset=mocked_get_queryset_result_for_plot_parameters.return_value.queryset,
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
        Then a `DataNotFoundForPlotError` is raised
        """
        # Given
        fake_chart_request_params = ChartRequestParams(
            plots=[fake_chart_plot_parameters],
            file_format="png",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])

        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundForPlotError):
            plots_interface.build_plot_data_from_parameters(
                plot_parameters=fake_chart_plot_parameters
            )

    @mock.patch.object(PlotsInterface, "get_queryset_result_for_plot_parameters")
    def test_build_plot_data_from_parameters_with_complete_queryset_delegates_call(
        self,
        spy_get_queryset_result_for_plot_parameters: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a set of `ChartParameters`
        When `build_plot_data_from_parameters_with_complete_queryset()`
            is called from an instance of `PlotsInterface`
        Then the call is delegated to the
            `get_queryset_result_for_plot_parameters()` method to fetch the data
        """
        # Given
        plots_interface = PlotsInterface(
            chart_request_params=mock.Mock(plots=[]),
            core_model_manager=mock.Mock(),
        )

        # When
        complete_plot_data: CompletePlotData = (
            plots_interface.build_plot_data_from_parameters_with_complete_queryset(
                plot_parameters=fake_chart_plot_parameters
            )
        )

        # Then
        spy_get_queryset_result_for_plot_parameters.assert_called_once_with(
            plot_parameters=fake_chart_plot_parameters
        )
        assert complete_plot_data.parameters == fake_chart_plot_parameters
        assert (
            complete_plot_data.queryset
            == spy_get_queryset_result_for_plot_parameters.return_value.queryset
        )

    def test_build_plot_data_from_parameters_with_complete_queryset_raises_error_when_no_data_found(
        self, fake_chart_plot_parameters: PlotParameters
    ):
        """
        Given a `PlotParameters` model requesting a plot
            for `CoreTimeSeries` data which cannot be found
        When `build_plot_data_from_parameters_with_complete_queryset()`
            is called from an instance of the `PlotsInterface`
        Then a `DataNotFoundForPlotError` is raised
        """
        # Given
        fake_chart_request_params = ChartRequestParams(
            plots=[fake_chart_plot_parameters],
            file_format="png",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])

        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundForPlotError):
            plots_interface.build_plot_data_from_parameters_with_complete_queryset(
                plot_parameters=fake_chart_plot_parameters
            )

    def test_get_headline_data_calls_core_headline_manager_with_correct_args(self):
        """
        Given a `CoreHeadlineManager`
        When `get_headline_data` is called from an instance of `PlotsInterface`
        Then the correct method is called from `CoreHeadlineManager` to retrieve headline data.
        """
        # Given
        spy_core_headline_manager = mock.Mock()
        mocked_x_axis = mock.Mock()
        mocked_y_axis = mock.Mock()
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()
        mocked_sex = mock.Mock()
        mocked_age = mock.Mock()
        mocked_chart_request_params = mock.MagicMock()
        mocked_chart_request_params.confidence_intervals = False

        plots_interface = PlotsInterface(
            chart_request_params=mocked_chart_request_params,
            core_model_manager=spy_core_headline_manager,
        )

        # When
        plots_params = {
            "fields_to_export": [mocked_x_axis, mocked_y_axis],
            "topic": mocked_topic,
            "metric": mocked_metric,
            "geography": mocked_geography,
            "geography_type": mocked_geography_type,
            "geography_code": "",
            "stratum": mocked_stratum,
            "sex": mocked_sex,
            "age": mocked_age,
        }
        headline_data = plots_interface.get_queryset_from_core_model_manager(
            plot_params=plots_params
        )

        # Then
        assert headline_data == spy_core_headline_manager.query_for_data.return_value
        spy_core_headline_manager.query_for_data.assert_called_once_with(
            fields_to_export=[mocked_x_axis, mocked_y_axis],
            topic=mocked_topic,
            metric=mocked_metric,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            geography_code="",
            stratum=mocked_stratum,
            sex=mocked_sex,
            age=mocked_age,
            rbac_permissions=mocked_chart_request_params.rbac_permissions,
        )

    def test_get_headline_data_calls_core_headline_manager_with_confidence_intervals(
        self,
    ):
        """
        Given a `CoreHeadlineManager`
        When `get_headline_data` is called from an instance of `PlotsInterface` with confidence intervals requested
        Then the correct method is called from `CoreHeadlineManager` to retrieve headline data with upper and lower confidence requested.
        """
        # Given
        spy_core_headline_manager = mock.Mock()
        mocked_x_axis = mock.Mock()
        mocked_y_axis = mock.Mock()
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()
        mocked_sex = mock.Mock()
        mocked_age = mock.Mock()
        mocked_chart_request_params = mock.MagicMock()
        mocked_chart_request_params.confidence_intervals = True

        plots_interface = PlotsInterface(
            chart_request_params=mocked_chart_request_params,
            core_model_manager=spy_core_headline_manager,
        )

        # When
        plots_params = {
            "fields_to_export": [
                mocked_x_axis,
                mocked_y_axis,
            ],
            "topic": mocked_topic,
            "metric": mocked_metric,
            "geography": mocked_geography,
            "geography_type": mocked_geography_type,
            "geography_code": "",
            "stratum": mocked_stratum,
            "sex": mocked_sex,
            "age": mocked_age,
        }

        headline_data = plots_interface.get_queryset_from_core_model_manager(
            plot_params=plots_params
        )

        # Then
        assert headline_data == spy_core_headline_manager.query_for_data.return_value
        spy_core_headline_manager.query_for_data.assert_called_once_with(
            fields_to_export=[
                mocked_x_axis,
                mocked_y_axis,
                "upper_confidence",
                "lower_confidence",
            ],
            topic=mocked_topic,
            metric=mocked_metric,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            geography_code="",
            stratum=mocked_stratum,
            sex=mocked_sex,
            age=mocked_age,
            rbac_permissions=mocked_chart_request_params.rbac_permissions,
        )

    @mock.patch(f"{MODULE_PATH}.auth.AUTH_ENABLED", True)
    def test_get_queryset_from_core_model_manager_passes_theme_and_topic_into_query_when_auth_enabled(
        self,
    ):
        """
        Given a `CoreHeadlineManager`
        When `get_headline_data` is called from an instance of `PlotsInterface`
        Then the correct method is called from `CoreHeadlineManager` to retrieve headline data.
        """
        # Given
        spy_core_headline_manager = mock.Mock()
        fake_metric = FakeMetricFactory.build_example_metric()
        fake_topic_manager = FakeTopicManager(topics=[fake_metric.topic])

        mocked_x_axis = mock.Mock()
        mocked_y_axis = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()
        mocked_sex = mock.Mock()
        mocked_age = mock.Mock()
        mocked_chart_request_params = mock.MagicMock()
        mocked_chart_request_params.confidence_intervals = False

        plots_interface = PlotsInterface(
            chart_request_params=mocked_chart_request_params,
            core_model_manager=spy_core_headline_manager,
            topic_model_manager=fake_topic_manager,
        )

        # When
        plots_params = {
            "fields_to_export": [mocked_x_axis, mocked_y_axis],
            "topic": fake_metric.topic.name,
            "metric": fake_metric.name,
            "geography": mocked_geography,
            "geography_type": mocked_geography_type,
            "geography_code": "",
            "stratum": mocked_stratum,
            "sex": mocked_sex,
            "age": mocked_age,
        }
        headline_data = plots_interface.get_queryset_from_core_model_manager(
            plot_params=plots_params
        )

        # Then
        assert headline_data == spy_core_headline_manager.query_for_data.return_value
        spy_core_headline_manager.query_for_data.assert_called_once_with(
            fields_to_export=[mocked_x_axis, mocked_y_axis],
            topic=fake_metric.topic.name,
            metric=fake_metric.name,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            geography_code="",
            stratum=mocked_stratum,
            sex=mocked_sex,
            age=mocked_age,
            rbac_permissions=mocked_chart_request_params.rbac_permissions,
            theme=fake_metric.topic.sub_theme.theme.name,
            sub_theme=fake_metric.topic.sub_theme.name,
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
        mocked_date_to = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()
        mocked_sex = mock.Mock()
        mocked_age = mock.Mock()
        mocked_chart_request_params = mock.MagicMock()
        mocked_chart_request_params.confidence_intervals = False

        plots_interface = PlotsInterface(
            chart_request_params=mocked_chart_request_params,
            core_model_manager=spy_core_time_series_manager,
        )

        # When
        plot_params = {
            "fields_to_export": [
                mocked_x_axis,
                mocked_y_axis,
                "in_reporting_delay_period",
            ],
            "field_to_order_by": mocked_x_axis,
            "topic": mocked_topic,
            "metric": mocked_metric,
            "date_from": mocked_date_from,
            "date_to": mocked_date_to,
            "geography": mocked_geography,
            "geography_type": mocked_geography_type,
            "stratum": mocked_stratum,
            "sex": mocked_sex,
            "age": mocked_age,
        }
        timeseries = plots_interface.get_queryset_from_core_model_manager(
            plot_params=plot_params
        )

        # Then
        assert timeseries == spy_core_time_series_manager.query_for_data.return_value
        spy_core_time_series_manager.query_for_data.assert_called_once_with(
            fields_to_export=[
                mocked_x_axis,
                mocked_y_axis,
                "in_reporting_delay_period",
            ],
            field_to_order_by=mocked_x_axis,
            topic=mocked_topic,
            metric=mocked_metric,
            date_from=mocked_date_from,
            date_to=mocked_date_to,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            stratum=mocked_stratum,
            sex=mocked_sex,
            age=mocked_age,
            rbac_permissions=mocked_chart_request_params.rbac_permissions,
        )

    @mock.patch.object(PlotsInterface, "get_queryset_from_core_model_manager")
    def test_get_queryset_result_for_plot_parameters_delegates_call_with_correct_args(
        self,
        mocked_get_queryset_from_core_model_manager: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model with a defined `date_from`
        When `get_queryset_result_for_plot_parameters()` is called
            from an instance of the `PlotsInterface`
        Then the call is delegated to the `get_timeseries()` method with the correct args
        """
        # Given
        date_from: str = "2023-01-01"
        fake_chart_plot_parameters.date_from = date_from

        plots_interface = PlotsInterface(
            chart_request_params=mock.MagicMock(),
            core_model_manager=mock.Mock(),
        )

        # When
        queryset_result: QuerySetResult = (
            plots_interface.get_queryset_result_for_plot_parameters(
                plot_parameters=fake_chart_plot_parameters
            )
        )

        # Then
        # The returned `QuerySetResult` is enriched via the `get_timeseries` method
        assert (
            queryset_result.queryset
            == mocked_get_queryset_from_core_model_manager.return_value
        )
        assert (
            queryset_result.latest_date
            == mocked_get_queryset_from_core_model_manager.return_value.latest_date
        )

        # The dict representation of the `PlotParameters` model
        # is unpacked into the `get_timeseries` method
        mocked_get_queryset_from_core_model_manager.assert_called_once_with(
            plot_params=fake_chart_plot_parameters.to_dict_for_query()
        )

    @mock.patch.object(PlotsInterface, "get_queryset_from_core_model_manager")
    def test_get_queryset_result_for_headline_plot_parameters_delegates_call_with_correct_args(
        self,
        mocked_get_queryset_from_core_model_manager: mock.MagicMock,
        fake_chart_plot_parameters_headline_data: PlotParameters,
    ):
        """
        Given a `PlotParameters` model with defined X and Y axis
        When `get_queryset_result_for_plot_parameters()` is called
        Then the call is delegated to the `get_headline_data()` method with the correct args
        """
        # Given
        fake_chart_request_params = mock.MagicMock()
        plots_interface = PlotsInterface(
            chart_request_params=fake_chart_request_params,
            core_model_manager=mock.MagicMock(),
        )

        # When
        queryset_result: QuerySetResult = (
            plots_interface.get_queryset_result_for_plot_parameters(
                plot_parameters=fake_chart_request_params
            )
        )

        # Then
        assert (
            queryset_result.queryset
            == mocked_get_queryset_from_core_model_manager.return_value
        )
        assert (
            queryset_result.latest_date
            == mocked_get_queryset_from_core_model_manager.return_value.latest_date
        )

    @mock.patch(f"{MODULE_PATH}.PlotValidation")
    def test_validate_plot_parameters_delegates_call_for_each_plot(
        self, spy_plot_validation: mock.MagicMock
    ):
        """
        Given a list of plot parameters on a mocked `PlotsCollection` model
        When `validate_plot_parameters()` is called
            from an instance of the `PlotsInterface`
        Then the call is delegated to and instance of `PlotValidation`
            for each plot parameters model

        Patches:
            `spy_plot_validation`: For the main assertion.
                The entire class is patched so that
                the init of the class can be checked
                as this is where the plot parameters are provided.
                As well as the subsequent `validate()` call.

        """
        # Given
        mocked_plot_parameters = [mock.Mock()] * 3
        mocked_chart_request_params = mock.Mock()
        mocked_chart_request_params.plots = mocked_plot_parameters
        plots_interface = PlotsInterface(
            chart_request_params=mocked_chart_request_params
        )

        # When
        plots_interface.validate_plot_parameters()

        # Then
        expected_calls = []
        for mocked_plot_parameter in mocked_plot_parameters:
            expected_calls += [
                mock.call(plot_parameters=mocked_plot_parameter),
                mock.call().validate(),
            ]

        spy_plot_validation.assert_has_calls(calls=expected_calls, any_order=True)

    def test_validate_plot_parameters_raises_error_if_metric_does_not_support_topic(
        self, fake_chart_request_params: ChartRequestParams
    ):
        """
        Given a mocked `PlotsCollection` model
            which contains a plot parameters model
            for an invalid metric and topic combination
        When the `PlotsInterface` is initialized
        Then an `InvalidPlotParametersError` is raised
        """
        # Given
        fake_chart_request_params.plots[0].topic = "RSV"
        fake_chart_request_params.plots[0].metric = "COVID-19_testing_PCRcountByDay"

        # When / Then
        with pytest.raises(InvalidPlotParametersError):
            plots_interface = PlotsInterface(
                chart_request_params=fake_chart_request_params
            )
            plots_interface.validate_plot_parameters()

    def test_validate_plot_parameters_raises_error_if_dates_are_not_in_correct_order(
        self, fake_chart_request_params: ChartRequestParams
    ):
        """
        Given a mocked `PlotsCollection` model
            which contains a plot parameters model
            for an invalid `date_from` and `date_to` selection
        When the `PlotsInterface` is initialized
        Then an `InvalidPlotParametersError` is raised

        """
        # Given
        fake_chart_request_params.plots[0].date_from = "2023-01-01"
        fake_chart_request_params.plots[0].date_to = "2022-12-31"

        # When / Then
        with pytest.raises(InvalidPlotParametersError):
            plots_interface = PlotsInterface(
                chart_request_params=fake_chart_request_params
            )
            plots_interface.validate_plot_parameters()

    @mock.patch.object(PlotsInterface, "validate_plot_parameters")
    def test_calls_validate_plot_parameters_during_init(
        self, spy_validate_plot_parameters: mock.MagicMock
    ):
        """
        Given a mocked `PlotCollection` model
        When an instance of the `PlotsInterface` is created
        Then the `validate_plot_parameters()` method is called

        Patches:
           `spy_validate_plot_parameters`: For the main assertion

        """
        # Given
        mocked_chart_request_params = mock.Mock()

        # When
        PlotsInterface(chart_request_params=mocked_chart_request_params)

        # Then
        spy_validate_plot_parameters.assert_called_once()


class TestGetAggregatedResults:
    @mock.patch(f"{MODULE_PATH}.aggregate_results_by_age")
    def test_can_delegate_call_to_aggregate_results_by_age(
        self,
        spy_aggregate_results_by_age: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model which requests `stratum` along the X-axis
        When `get_aggregated_results()` is called
        Then the call is delegated to `aggregate_results_by_age()`
        """
        # Given
        fake_chart_plot_parameters.x_axis = ChartAxisFields.age.name
        mocked_queryset = mock.Mock()

        # When
        aggregated_results = get_aggregated_results(
            plot_parameters=fake_chart_plot_parameters, queryset=mocked_queryset
        )

        # Then
        assert aggregated_results == spy_aggregate_results_by_age.return_value
        spy_aggregate_results_by_age.assert_called_once_with(queryset=mocked_queryset)

    @pytest.mark.parametrize(
        "x_axis",
        [
            ChartAxisFields.date.name,
            ChartAxisFields.metric.name,
        ],
    )
    @mock.patch(f"{MODULE_PATH}.aggregate_results")
    def test_delegates_call_to_unzip_values(
        self,
        spy_aggregate_results: mock.MagicMock,
        x_axis: str,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model which does not request `stratum` along the X-axis
        When `get_aggregated_results()` is called
        Then the call is delegated to `aggregate_results()`
        """
        # Given
        mocked_queryset = mock.Mock()
        fake_chart_plot_parameters.x_axis = x_axis

        # When
        x_and_y_values = get_aggregated_results(
            plot_parameters=fake_chart_plot_parameters, queryset=mocked_queryset
        )

        # Then
        assert x_and_y_values == spy_aggregate_results.return_value
        spy_aggregate_results.assert_called_once_with(values=mocked_queryset)


class TestConvertType:
    @pytest.mark.parametrize(
        "mock_input, mock_output",
        [
            ("85", 85),
            ("04", 4),
            ("default", "default"),
        ],
    )
    def test_basic_operation(self, mock_input: str, mock_output: int | str):
        """
        Given a string that may or may not contain a number
        When `convert_type()` is called
        Then expected result is returned
        """
        # Given/When
        actual_output = convert_type(s=mock_input)

        # Then
        assert mock_output == actual_output


class TestSortByAge:
    def test_returns_correct_results(self):
        """
        Given a queryset containing age based results
        When `sort_by_age()` is called
        Then the result is a dictionary of aggregated results
            with human-readable labels for the age values
        """
        # Given
        fake_queryset = FakeQuerySet(
            [
                {
                    "age__name": "00-04",
                    "metric_value": Decimal("1.0"),
                    "in_reporting_delay_period": False,
                },
                {
                    "age__name": "55+",
                    "metric_value": Decimal("2.0"),
                    "in_reporting_delay_period": False,
                },
                {
                    "age__name": "all",
                    "metric_value": Decimal("3.0"),
                    "in_reporting_delay_period": False,
                },
            ]
        )

        # When
        aggregated_results = aggregate_results_by_age(queryset=fake_queryset)

        # Then
        assert aggregated_results["age__name"] == [
            "00 - 04",
            "55+",
            "all",
        ]
        assert aggregated_results["metric_value"] == [1, 2, 3]


class TestBuildAgeDisplayName:
    @pytest.mark.parametrize(
        "input_value, expected_value",
        [("00-04", "00 - 04"), ("10-14", "10 - 14"), ("90+", "90+"), ("all", "all")],
    )
    def test_returns_correct_value(self, input_value: str, expected_value: str):
        """
        Given a value
        When `_build_age_display_name()` is called
        Then the correct value is returned
        """
        # Given
        value = input_value

        # When
        cast_value = _build_age_display_name(value=value)

        # Then
        assert cast_value == expected_value
