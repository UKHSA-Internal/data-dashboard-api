import datetime
from unittest import mock

from metrics.domain.models import PlotParameters, PlotsCollection
from metrics.domain.tables.generation import TabularData
from metrics.interfaces.tables.access import (
    TablesInterface,
    generate_table_for_full_plots,
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

    @mock.patch.object(TabularData, "create_tabular_plots")
    def test_generate_full_plots_for_table(
        self,
        spy_create_tabular_plots: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotsCollection` and a `CoreTimeSeriesManager`
        When a `generate_full_plots_for_table()`
            is called from an instance of `TablesInterface`
        Then the `PlotsInterface` is called to get the plots data
        And the call is delegated to the `create_tabular_plots()` method
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
        table_plots: list[
            dict[str, str]
        ] = tables_interface.generate_full_plots_for_table()

        # Then
        spy_create_tabular_plots.assert_called_once()
        assert table_plots == spy_create_tabular_plots.return_value


class TestGenerateTableForFullPlots:
    @mock.patch.object(TablesInterface, "generate_full_plots_for_table")
    def test_delegates_call_for_producing_table(
        self,
        spy_generate_full_plots_for_table: mock.MagicMock,
        fake_plots_collection: PlotsCollection,
    ):
        """
        Given a fake `PlotsCollection` model
        When `generate_table_for_full_plots()` is called
        Then `generate_full_plots_for_table` is called
            from an instance of the `TablesInterface`

        Patches:
            `spy_generate_full_plots_for_table`: For the main assertions

        """
        # Given
        plots_collection = fake_plots_collection

        # When
        table = generate_table_for_full_plots(plots_collection=plots_collection)

        # Then
        assert table == spy_generate_full_plots_for_table.return_value
        spy_generate_full_plots_for_table.assert_called_once()
