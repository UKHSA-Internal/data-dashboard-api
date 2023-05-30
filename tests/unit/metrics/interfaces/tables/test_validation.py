from unittest import mock

from metrics.interfaces.tables import validation


class TestTablesValidation:
    def test_plots_interface_is_created_with_correct_args_by_default(self):
        """
        Given a `PlotParameters` model
        When an instance of the `TablesValidation` is created
            without explicitly providing a `PlotValidation`
        Then an instance of the `PlotValidation` is created with the correct args
        """
        # Given
        mocked_plot_parameters = mock.MagicMock()

        # When
        tables_validation = validation.TablesValidation(
            plot_parameters=mocked_plot_parameters,
        )

        # Then
        created_plot_validation = tables_validation.plot_validation
        assert created_plot_validation.plot_parameters == mocked_plot_parameters
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
