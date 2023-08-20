import datetime
from unittest import mock

import pytest

from metrics.domain.models import PlotParameters, PlotsCollection
from metrics.domain.utils import ChartAxisFields
from metrics.interfaces.tables.access import (
    TablesInterface,
    generate_table,
    generate_table_v3,
)
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager

MODULE_PATH = "metrics.interfaces.tables.access"


class TestTablesInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(chart_plot_parameters: PlotParameters):
        return [
            FakeCoreTimeSeriesFactory.build_time_series(
                date=datetime.date(year=2023, month=2, day=i + 1),
                metric_name=chart_plot_parameters.metric_name,
                topic_name=chart_plot_parameters.topic_name,
                stratum_name=chart_plot_parameters.stratum_name,
            )
            for i in range(10)
        ]

    def test_plots_interface_is_created_with_correct_args_by_default(self):
        """
        Given a `PlotsCollection` and a `CoreTimeSeriesManager`
        When an instance of the `TablesInterface` is created
            without explicitly providing a `PlotsInterface`
        Then an instance of the `PlotsInterface` is created with the correct args
        """
        # Given
        mocked_plots_collection = mock.MagicMock()
        mocked_core_time_series_manager = mock.Mock()

        # When
        tables_interface = TablesInterface(
            plots_collection=mocked_plots_collection,
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # Then
        created_plots_interface = tables_interface.plots_interface
        assert created_plots_interface.plots_collection == mocked_plots_collection
        assert (
            created_plots_interface.core_time_series_manager
            == mocked_core_time_series_manager
        )

    @mock.patch.object(TablesInterface, "generate_plots_for_table")
    def test_generate_plots_for_table(
        self,
        spy_create_plots_in_tabular_format: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotsCollection` and a `CoreTimeSeriesManager`
        When a `generate_plots_for_table()` is called from the `TablesInterface`
        Then the `PlotsInterface` is called to get the plots data
        And the call is delegated to the `create_plots_in_tabular_format()`
        """
        # Given
        fake_core_time_series = self._setup_fake_time_series_for_plot(
            chart_plot_parameters=valid_plot_parameters
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(fake_core_time_series)

        plots_collection = PlotsCollection(
            plots=[valid_plot_parameters],
            file_format="svg",
            chart_height=123,
            chart_width=456,
            x_axis="date",
            y_axis="metric",
        )

        tables_interface = TablesInterface(
            plots_collection=plots_collection,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        table_plots: list[dict[str, str]] = tables_interface.generate_plots_for_table()

        # Then
        spy_create_plots_in_tabular_format.assert_called_once()
        assert table_plots == spy_create_plots_in_tabular_format.return_value


class TestGenerateTables:
    @mock.patch.object(TablesInterface, "generate_plots_for_table")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_table_plot")
    def test_delegates_call_for_validation(
        self,
        spy_validate_each_requested_table_plot: mock.MagicMock,
        mocked_generate_plots_for_table: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_table()` is called
        Then a call is delegated to `validate_each_requested_table_plot()` for validation purposes
        And `generate_plots_for_table` is called from an instance of the `TablesInterface`

        Patches:
            `spy_validate_each_requested_table_plot`: For the main assertion
            `mocked_generate_plots_for_table`: Removal of table generation logic
        """
        # Given
        mocked_plots_collection = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_table(plots_collection=mocked_plots_collection)

        # Then
        spy_validate_each_requested_table_plot.assert_called_once_with(
            plots_collection=mocked_plots_collection
        )

    @mock.patch.object(TablesInterface, "generate_plots_for_table")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_table_plot")
    def test_delegates_call_for_producing_table(
        self,
        mocked_validate_each_requested_table_plot: mock.MagicMock,
        spy_generate_plots_for_table: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_table()` is called
        Then a call is delegated to `validate_each_requested_table_plot()` for validation purposes
        And `generate_plots_for_table` is called from an instance of the `TablesInterface`

        Patches:
            `mocked_validate_each_requested_table_plot`: Removal of validation side effects
            `spy_generate_plots_for_table`: For the main assertions
        """
        # Given
        mocked_plots_collection = mock.MagicMock(plots=[mock.Mock()])

        # When
        table = generate_table(plots_collection=mocked_plots_collection)

        # Then
        assert table == spy_generate_plots_for_table.return_value
        spy_generate_plots_for_table.assert_called_once()


class TestGenerateTableV2:
    @pytest.mark.parametrize(
        "explicit_column_header_value",
        [chart_axis_field.name for chart_axis_field in ChartAxisFields],
    )
    @mock.patch(f"{MODULE_PATH}.generate_table")
    def test_sets_generic_key(
        self, mocked_generate_table: mock.MagicMock, explicit_column_header_value: str
    ):
        """
        Given `generate_table` which returns expected tabular output
        When `generate_table_v2()` is called
        Then returned output does contain an explicit key like `date` or `stratum`
        """
        # Given
        mocked_plots_collection = mock.Mock()
        mocked_generate_table.return_value = [
            {
                explicit_column_header_value: "2022-09-05",
                "values": [
                    {"label": "Plot1", "value": "10"},
                    {"label": "Plot2", "value": "11"},
                ],
            },
        ]

        # When
        generated_table: list[dict[str, str]] = generate_table_v3(
            plots_collection=mocked_plots_collection
        )

        # Then
        expected_table: list[dict[str, str]] = [
            {
                "heading_value": "2022-09-05",
                "values": [
                    {"label": "Plot1", "value": "10"},
                    {"label": "Plot2", "value": "11"},
                ],
            },
        ]
        assert generated_table == expected_table
