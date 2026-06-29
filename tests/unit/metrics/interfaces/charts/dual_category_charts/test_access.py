import datetime
from unittest import mock

import pytest

from metrics.data.managers.core_models.headline import CoreHeadlineManager
from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
    StaticFields,
)
from metrics.domain.models.plots import ChartGenerationPayload, PlotParameters
from metrics.interfaces.charts.common.chart_output import ChartOutput
from metrics.interfaces.charts.dual_category_charts.access import (
    DualCategoryChartsInterface,
)
from metrics.interfaces.plots.access import PlotsInterface

MODULE_PATH = "metrics.interfaces.charts.dual_category_charts.access"


@pytest.fixture
def dual_category_chart_request_params(
    fake_chart_plot_parameters: PlotParameters,
) -> DualCategoryChartRequestParams:
    return DualCategoryChartRequestParams(
        chart_type="stacked_bar",
        secondary_category="age",
        primary_field_values=["m"],
        static_fields=StaticFields(
            topic=fake_chart_plot_parameters.topic,
            metric=fake_chart_plot_parameters.metric,
            geography="England",
            geography_type="Nation",
            age="all",
            sex="all",
            stratum="default",
            date_from="2020-02-01",
            date_to="2021-02-01",
        ),
        plots=[fake_chart_plot_parameters],
        file_format="svg",
        chart_width=320,
        chart_height=200,
        x_axis="sex",
        y_axis="metric",
    )


@pytest.fixture
def dual_category_chart_request_params_headline(
    fake_chart_plot_parameters_headline_data: PlotParameters,
) -> DualCategoryChartRequestParams:
    plot = fake_chart_plot_parameters_headline_data
    return DualCategoryChartRequestParams(
        chart_type="stacked_bar",
        secondary_category="age",
        primary_field_values=["all"],
        static_fields=StaticFields(
            topic=plot.topic,
            metric=plot.metric,
            geography="England",
            geography_type="Nation",
            age="all",
            sex="all",
            stratum="default",
            date_from="",
            date_to="",
        ),
        plots=[plot],
        file_format="svg",
        chart_width=320,
        chart_height=200,
        x_axis="age",
        y_axis="metric",
    )


class TestDualCategoryChartsInterface:
    def test_set_latest_date_from_plots_data_fails_silently_when_latest_date_not_provided(
        self,
        dual_category_chart_request_params: DualCategoryChartRequestParams,
    ):
        """
        Given plot data with no valid latest dates
        When `_set_latest_date_from_plots_data()` is called
        Then `last_updated` is left unchanged
        """
        # Given
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params,
        )
        original_last_updated = "2024-01-01"
        charts_interface.last_updated = original_last_updated
        mocked_plots_data = [mock.MagicMock(latest_date=None) for _ in range(3)]

        # When
        charts_interface._set_latest_date_from_plots_data(plots_data=mocked_plots_data)

        # Then
        assert charts_interface.last_updated == original_last_updated

    def test_initialises_core_model_manager_with_headline_manager(
        self,
        dual_category_chart_request_params_headline: DualCategoryChartRequestParams,
    ):
        """
        Given a dual category chart request for headline data
        When a `DualCategoryChartsInterface` is created
        Then the `core_model_manager` is a `CoreHeadlineManager`
        """
        # When
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params_headline,
        )

        # Then
        assert isinstance(charts_interface.core_model_manager, CoreHeadlineManager)

    def test_initialises_core_model_manager_with_timeseries_manager(
        self,
        dual_category_chart_request_params: DualCategoryChartRequestParams,
    ):
        """
        Given a dual category chart request for timeseries data
        When a `DualCategoryChartsInterface` is created
        Then the `core_model_manager` is a `CoreTimeSeriesManager`
        """
        # When
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params,
        )

        # Then
        assert isinstance(charts_interface.core_model_manager, CoreTimeSeriesManager)

    @mock.patch(f"{MODULE_PATH}.generate_stacked_bar")
    def test_build_chart_figure_delegates_call_to_generate_stacked_bar(
        self,
        mock_generate_stacked_bar: mock.MagicMock,
        dual_category_chart_request_params: DualCategoryChartRequestParams,
        fake_plot_data,
    ):
        """
        Given a valid `chart_generation_payload`
        When `_build_chart_figure()` is called
        Then a call is made to `generate_stacked_bar`
        """
        # Given
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params,
        )
        chart_generation_payload = ChartGenerationPayload(
            chart_width=320,
            chart_height=200,
            plots=[fake_plot_data],
            x_axis_title="Date",
            y_axis_title="Cases",
            secondary_category="age",
        )

        # When
        charts_interface._build_chart_figure(
            chart_generation_payload=chart_generation_payload,
        )

        # Then
        mock_generate_stacked_bar.assert_called_once_with(
            chart_generation_payload=chart_generation_payload,
        )

    @mock.patch.object(PlotsInterface, "build_plots_data")
    def test_build_chart_plots_data_delegates_call_to_plots_interface(
        self,
        spy_build_plots_data: mock.MagicMock,
        dual_category_chart_request_params: DualCategoryChartRequestParams,
        fake_plot_data,
    ):
        """
        Given a valid dual category chart request
        When `_build_chart_plots_data()` is called
        Then a call is made to `PlotsInterface.build_plots_data`
        """
        # Given
        fake_plot_data.latest_date = datetime.date(2024, 1, 1)
        spy_build_plots_data.return_value = [fake_plot_data]
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params,
        )

        # When
        plots_data = charts_interface._build_chart_plots_data()

        # Then
        spy_build_plots_data.assert_called_once()
        assert plots_data == spy_build_plots_data.return_value

    def test_set_latest_date_from_plots_data_sets_last_updated(
        self,
        dual_category_chart_request_params: DualCategoryChartRequestParams,
    ):
        """
        Given plot data with valid latest dates
        When `_set_latest_date_from_plots_data()` is called
        Then `last_updated` is set to the latest date
        """
        # Given
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params,
        )
        latest_date = datetime.date(2024, 6, 1)
        mocked_plots_data = [
            mock.MagicMock(latest_date=datetime.date(2024, 1, 1)),
            mock.MagicMock(latest_date=latest_date),
        ]

        # When
        charts_interface._set_latest_date_from_plots_data(plots_data=mocked_plots_data)

        # Then
        assert charts_interface.last_updated == "2024-06-01"

    @mock.patch.object(DualCategoryChartsInterface, "_build_chart_generation_payload")
    @mock.patch.object(DualCategoryChartsInterface, "_build_chart_figure")
    def test_generate_chart_output_returns_instance_of_chart_output(
        self,
        mock_build_chart_figure: mock.MagicMock,
        mock_build_chart_generation_payload: mock.MagicMock,
        dual_category_chart_request_params: DualCategoryChartRequestParams,
        fake_plot_data,
    ):
        """
        Given a valid dual category chart request
        When `generate_chart_output()` is called
        Then an instance of `ChartOutput` is returned
        """
        # Given
        mock_build_chart_generation_payload.return_value = ChartGenerationPayload(
            chart_width=320,
            chart_height=200,
            plots=[fake_plot_data],
            x_axis_title="Date",
            y_axis_title="Cases",
            secondary_category="age",
        )
        charts_interface = DualCategoryChartsInterface(
            chart_request_params=dual_category_chart_request_params,
        )

        # When
        chart_output = charts_interface.generate_chart_output()

        # Then
        assert isinstance(chart_output, ChartOutput)
        assert chart_output.figure == mock_build_chart_figure.return_value
