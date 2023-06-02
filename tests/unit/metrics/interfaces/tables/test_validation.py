from unittest import mock

from metrics.domain.models import PlotParameters, PlotsCollection
from metrics.interfaces.tables import validation
from metrics.interfaces.tables.validation import (
    TablesValidation,
    validate_each_requested_table_plot,
    validate_table_plot_parameters,
)

MODULE_PATH = "metrics.interfaces.tables.validation"


class TestTablesValidation:
    def test_plots_interface_is_created_with_correct_args_by_default(self):
        """
        Given a `PlotParameters` model
        When an instance of the `TablesValidation` is created
            without explicitly providing a `PlotValidation`
        Then an instance of the `PlotValidation` is created with the correct args
        """
        # Given
        mocked_plot_parameters = mock.Mock()

        # When
        tables_validation = validation.TablesValidation(
            plot_parameters=mocked_plot_parameters,
        )

        # Then
        created_plot_validation = tables_validation.plot_validation
        # The `PlotParameters` model is passed to the `PlotValidation` instance
        assert created_plot_validation.plot_parameters == mocked_plot_parameters

        # The model managers are provided to the `PlotValidation`
        assert (
            created_plot_validation.core_time_series_manager
            == tables_validation.core_time_series_manager
        )
        assert (
            created_plot_validation.metric_manager == tables_validation.metric_manager
        )


class TestValidate:
    def test_delegates_to_correct_validators(self):
        """
        Given an instance of the `TablesValidation`
        When `validate()` is called
        Then the correct sub validate methods are called and delegated to
        """
        # Given
        spy_plot_validation = mock.Mock()
        tables_validation = validation.TablesValidation(
            plot_parameters=mock.Mock(),
            plot_validation=spy_plot_validation,
        )

        # When
        tables_validation.validate()

        # Then
        # General plot delegated validation
        spy_plot_validation.validate.assert_called_once()


class TestValidateEachRequestedChartPlot:
    @mock.patch(f"{MODULE_PATH}.validate_table_plot_parameters")
    def test_delegates_call_for_each_chart_plot(
        self,
        spy_validate_table_plot_parameters: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
        fake_chart_plot_parameters_covid_cases: PlotParameters,
    ):
        """
        Given a `PlotsCollection` model requesting plots
            of multiple `PlotParameters` models
        When `validate_each_requested_table_plot()` is called
        Then the call is delegated to `validate_table_plot_parameters()`
            for each `PlotParameters` models
        """
        # Given
        plots = [
            fake_chart_plot_parameters,
            fake_chart_plot_parameters_covid_cases,
        ]
        plots_collection = PlotsCollection(
            file_format="svg",
            plots=plots,
            chart_width=123,
            chart_height=456,
        )

        # When
        validate_each_requested_table_plot(plots_collection=plots_collection)

        # Then
        expected_calls = [
            mock.call(plot_parameters=requested_plot_parameters)
            for requested_plot_parameters in plots
        ]
        spy_validate_table_plot_parameters.assert_has_calls(calls=expected_calls)


class TestValidateTablePlotParameters:
    @mock.patch.object(TablesValidation, "validate")
    def test_delegates_call_to_validate_method_on_tables_validation_class(
        self,
        spy_validate_method: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model
        When `validate_table_plot_parameters()` is called
        Then the call is delegated to the `validate()` from an instance of the `TablesValidation`
        """
        # Given
        plot_parameters = fake_chart_plot_parameters

        # When
        validate_table_plot_parameters(plot_parameters=plot_parameters)

        # Then
        spy_validate_method.assert_called_once()
