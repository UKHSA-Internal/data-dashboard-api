from unittest import mock

import pytest

from metrics.domain.models import PlotParameters
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts import validation


class TestChartsValidator:
    def test_plots_interface_is_created_with_correct_args_by_default(self):
        """
        Given a `PlotParameters` model
        When an instance of the `ChartsRequestValidator` is created
            without explicitly providing a `PlotValidation`
        Then an instance of the `PlotValidation` is created with the correct args
        """
        # Given
        mocked_plot_parameters = mock.Mock()

        # When
        charts_validation = validation.ChartsRequestValidator(
            plot_parameters=mocked_plot_parameters,
        )

        # Then
        created_plot_validation = charts_validation.plot_validation
        # The `PlotParameters` model is passed to the `PlotValidation` instance
        assert created_plot_validation.plot_parameters == mocked_plot_parameters

        # The model managers are provided to the `PlotValidation`
        assert (
            created_plot_validation.core_time_series_manager
            == charts_validation.core_time_series_manager
        )
        assert (
            created_plot_validation.metric_manager == charts_validation.metric_manager
        )


class TestValidate:
    @mock.patch.object(
        validation.ChartsRequestValidator,
        "_validate_series_type_chart_works_with_metric",
    )
    def test_delegates_to_correct_validators(
        self,
        spy_validate_series_type_chart_works_with_metric: mock.MagicMock,
    ):
        """
        Given an instance of the `ChartsRequestValidator`
        When `validate()` is called
        Then the correct sub validate methods are called and delegated to
        """
        # Given
        spy_plot_validation = mock.Mock()
        validator = validation.ChartsRequestValidator(
            plot_parameters=mock.Mock(),
            plot_validation=spy_plot_validation,
        )

        # When
        validator.validate()

        # Then
        # Charts-specific delegated validation
        spy_validate_series_type_chart_works_with_metric.assert_called_once()

        # General plot delegated validation
        spy_plot_validation.validate.assert_called_once()


class TestValidateSeriesChartTypeWorksWithMetric:
    def test_delegates_validation_to_plot_validation(self):
        """
        Given a metric of `new_cases_daily` and a request for a `simple_line` type chart
        When `_validate_series_type_chart_works_with_metric()` is called from an instance of `ChartsRequestValidator`
        The call is delegated to the `PlotValidation` object
        Then None is returned
        """
        # Given
        metric = "new_cases_daily"
        chart_type = ChartTypes.simple_line.value
        plot_parameters = PlotParameters(
            metric=metric,
            topic="COVID-19",
            chart_type=chart_type,
        )
        spy_plot_validation = mock.Mock()

        validator = validation.ChartsRequestValidator(
            plot_parameters=plot_parameters,
            plot_validation=spy_plot_validation,
        )

        # When
        validated = validator._validate_series_type_chart_works_with_metric()

        # Then
        assert validated is None
        # Check that the call to validate the metric being okay was delegated to the `PlotValidation` object
        assert spy_plot_validation.method_calls == [
            mock.call._does_metric_have_multiple_records()
        ]

    def test_passes_naively_if_non_series_chart_type_provided(self):
        """
        Given a metric of `new_cases_daily` and a request for a `waffle` type chart
        When `_validate_series_type_chart_works_with_metric()` is called from an instance of `ChartsRequestValidator`
        Then None is returned
        """
        # Given
        metric = "new_cases_daily"
        chart_type = ChartTypes.waffle.value
        plot_parameters = PlotParameters(
            metric=metric,
            topic="COVID-19",
            chart_type=chart_type,
        )

        validator = validation.ChartsRequestValidator(plot_parameters=plot_parameters)
        # Here we don't need to stub out the managers or the plot validation
        # because the method under test should simply use the `chart_type`
        # attribute of the `PlotParameters` object

        # When
        validated = validator._validate_series_type_chart_works_with_metric()

        # Then
        assert validated is None

    def test_can_raise_error_for_invalid_combination(self):
        """
        Given a metric of `covid_occupied_beds_latest` and a request for a `simple_line` type chart
        And the call delegated to the `PlotValidation` object returns False
        When `_validate_series_type_chart_works_with_metric()` is called from an instance of `ChartsRequestValidator`
        Then a `ChartTypeDoesNotSupportMetricError` is raised
        """
        # Given
        metric = "covid_occupied_beds_latest"
        chart_type = ChartTypes.simple_line.value
        plot_parameters = PlotParameters(
            metric=metric,
            topic="COVID-19",
            chart_type=chart_type,
        )

        mocked_plot_validation = mock.Mock()
        mocked_plot_validation._does_metric_have_multiple_records.return_value = False

        validator = validation.ChartsRequestValidator(
            plot_parameters=plot_parameters,
            plot_validation=mocked_plot_validation,
        )

        # When / Then
        expected_error_message = (
            f"`{metric}` is not compatible with `{chart_type}` chart types"
        )
        with pytest.raises(
            validation.ChartTypeDoesNotSupportMetricError, match=expected_error_message
        ):
            validator._validate_series_type_chart_works_with_metric()


class TestIsChartSeriesType:
    def test_waffle_chart_returns_false(self, valid_plot_parameters: PlotParameters):
        """
        Given a chart type of `waffle`
        When `is_chart_series_type()` is called from an instance of `ChartsRequestValidator`
        Then False is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        plot_parameters.chart_type = ChartTypes.waffle.value

        validator = validation.ChartsRequestValidator(plot_parameters=plot_parameters)

        # When
        chart_is_series_type: bool = validator._is_chart_series_type()

        # Then
        assert not chart_is_series_type

    @pytest.mark.parametrize(
        "time_series_chart_type",
        [ChartTypes.simple_line.value, ChartTypes.line_with_shaded_section.value],
    )
    def test_line_charts_returns_true(
        self, time_series_chart_type: str, valid_plot_parameters: PlotParameters
    ):
        """
        Given a line/timeseries chart type
        When `is_chart_series_type()` is called from an instance of `ChartsRequestValidator`
        Then True is returned
        """
        # Given
        plot_parameters = valid_plot_parameters
        plot_parameters.chart_type = time_series_chart_type

        validator = validation.ChartsRequestValidator(plot_parameters=plot_parameters)

        # When
        chart_is_series_type: bool = validator._is_chart_series_type()

        # Then
        assert chart_is_series_type
