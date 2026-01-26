import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.domain.charts.colour_scheme import RGBAChartLineColours

from metrics.domain.charts.common_charts.plots.line_multi_coloured.properties import (
    ChartLineTypes,
)
from metrics.domain.models import PlotGenerationData
from metrics.domain.models.plots import (
    NoReportingDelayPeriodFoundError,
    ReportingDelayNotProvidedToPlotsError,
)
from metrics.domain.models.plots_text import PlotsText
from metrics.domain.common.utils import ChartTypes

MODULE_PATH = "metrics.domain.models.plots_text"


class TestPlotsText:
    def test_returns_correct_text_for_no_plots(self):
        """
        Given an empty list of `PlotData` models
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text states there is no data available.
        """
        # Given
        empty_plots_data = []
        plots_text = PlotsText(plots_data=empty_plots_data)

        # When
        text: str = plots_text.construct_text()

        # Then
        assert text == "There is no data being shown for this chart."

    def test_returns_correct_text_for_plots_with_no_data(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of `PlotData` models of which have no data
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text states there is no data available.
        """
        # Given
        fake_plot_data.x_axis_values = []
        fake_plot_data.y_axis_values = []
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        assert text == "There is no data being shown for this chart."

    def test_returns_correct_text_about_parameters_for_one_plot(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of 1 enriched `PlotData` model
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for the plot
        """
        # Given
        label = "COVID-19 deaths in London"
        fake_plot_data.parameters.chart_type = ChartTypes.line_multi_coloured.value
        fake_plot_data.parameters.label = label
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_parameters = (
            f"There is only 1 plot on this chart. "
            f"The horizontal X-axis is labelled '{fake_plot_data.parameters.x_axis}'. "
            f"Whilst the vertical Y-axis is labelled '{fake_plot_data.parameters.y_axis}'. "
            f"This is a {fake_plot_data.parameters.line_colour_enum.presentation_name} "
            f"{fake_plot_data.parameters.line_type.lower()} line plot. "
            f"The plot has a label of '{label}'. "
            f"This plot shows data for {fake_plot_data.parameters.topic}. "
            f"Specifically the metric '{fake_plot_data.parameters.metric}' "
            f"for the {fake_plot_data.parameters.geography} area, "
            f"along with the age banding of '{fake_plot_data.parameters.age}' "
            f"for the gender group of {fake_plot_data.parameters.sex}. "
        )
        assert expected_text_about_parameters in text

    def test_returns_correct_line_colour_when_not_provided_for_one_plot(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of 1 enriched `PlotData` model
            which does not declare a `line_colour` or `line_type`
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for the plot.
            Including the fallback parameters
            for line colour and type
        """
        # Given
        fake_plot_data.parameters.line_colour = ""
        fake_plot_data.parameters.line_type = ""

        fake_plot_data.parameters.chart_type = ChartTypes.line_multi_coloured.value
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_parameters = (
            f"This is a {RGBAChartLineColours.BLACK.name.lower()} "
            f"{ChartLineTypes.SOLID.value.lower()} line plot. "
        )
        assert expected_text_about_parameters in text

    @pytest.mark.parametrize(
        "trend_line_colour, trend_type",
        [
            ("TREND_LINE_POSITIVE", "positive"),
            ("TREND_LINE_NEGATIVE", "negative"),
            ("TREND_LINE_NEUTRAL", "neutral"),
        ],
    )
    def test_returns_correct_trend_type_when_line_colour_provided_is_for_trend_line(
        self,
        fake_plot_data: PlotGenerationData,
        trend_line_colour: str,
        trend_type: str,
    ):
        """
        Given a valid plot where the `line_colour` is a trend line option
        When the `construct_text()` method is called
        Then the correct trend type is returned in the response.
        """
        fake_plot_data.parameters.line_colour = trend_line_colour
        fake_plot_data.parameters.line_type = "SOLID"
        fake_plot_data.parameters.chart_type = ChartTypes.line_single_simplified.value
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_parameters = (
            f"This is a solid line chart, showing a {trend_type} trend in the data."
        )
        assert expected_text_about_parameters in text

    def test_returns_no_trend_type_when_line_colour_is_trend_line_none(
        self,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given a valid plot where the `line_colour` that is not a `TREND_LINE` colour
        When the `construct_text()` method is called
        Then no trend type is returned in the response.
        """
        fake_plot_data.parameters.line_colour = "COLOUR_1_DARK_BLUE"
        fake_plot_data.parameters.line_type = "SOLID"
        fake_plot_data.parameters.chart_type = ChartTypes.line_single_simplified.value
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_parameters = "This is a solid line chart,"
        assert expected_text_about_parameters in text

    def test_returns_correct_text_about_parameters_for_multiple_plots(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of 3 enriched `PlotData` models
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for each plot
        """
        # Given
        second_plot_data = fake_plot_data.model_copy(deep=True)
        second_plot_data.parameters.topic = "Influenza"
        second_plot_data.parameters.metric = "influenza_testing_positivityByWeek"
        second_plot_data.parameters.sex = "f"
        second_plot_data.parameters.age = "0_4"
        second_plot_data.parameters.line_type = "DASH"

        third_plot_data = fake_plot_data.model_copy(deep=True)
        third_plot_data.parameters.chart_type = "bar"
        third_plot_data.parameters.metric = "influenza_testing_positivityByWeek"
        third_plot_data.parameters.sex = "m"
        third_plot_data.parameters.label = "Influenza testing for Males"

        plots_text = PlotsText(
            plots_data=[fake_plot_data, second_plot_data, third_plot_data]
        )

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_intro = (
            "There are 3 plots on this chart. "
            "The horizontal X-axis is labelled 'metric'. Whilst the vertical Y-axis is labelled 'date'. "
        )
        expected_plot_1_params_description = (
            "This is plot number 1 on this chart. "
            "This is a dark blue solid line plot. "
            "This plot shows data for COVID-19. "
            "Specifically the metric 'COVID-19_deaths_ONSByDay' for the London area, "
            "along with the age banding of 'all' for the gender group of all. "
        )
        expected_plot_2_params_description = (
            "This is plot number 2 on this chart. "
            "This is a dark blue dash line plot. "
            "This plot shows data for Influenza. "
            "Specifically the metric 'influenza_testing_positivityByWeek' "
            "for the London area, "
            "along with the age banding of '0_4' for the gender group of females. "
        )
        expected_plot_3_params_description = (
            "This is plot number 3 on this chart. "
            "This is a dark blue solid bar plot. "
            "The plot has a label of 'Influenza testing for Males'. "
            "This plot shows data for COVID-19. "
            "Specifically the metric 'influenza_testing_positivityByWeek' "
            "for the London area, "
            "along with the age banding of 'all' for the gender group of males. "
        )

        assert expected_intro in text
        assert expected_plot_1_params_description in text
        assert expected_plot_2_params_description in text
        assert expected_plot_3_params_description in text

    def test_returns_correct_text_about_data_for_one_plot(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of 1 enriched `PlotData` model
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text provides commentary
            about the data being shown by the plot
        """
        # Given
        fake_plot_data.x_axis_values = [
            datetime.date(year=2023, month=1, day=i + 1)
            for i in range(len(fake_plot_data.y_axis_values))
        ]
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_plot_data = (
            "This plot shows data from 01 January 2023 to 12 January 2023. "
            "It rose from 1.0 on 01 January 2023 to 2.0 on 02 January 2023. "
            "It rose from 4.0 on 03 January 2023 to 5.0 on 04 January 2023. "
            "It fell from 5.0 on 05 January 2023 to 2.0 on 06 January 2023. "
            "It rose from 1.0 on 07 January 2023 to 8.0 on 08 January 2023. "
            "It rose from 9.0 on 09 January 2023 to 10.0 on 10 January 2023. "
            "And finally. "
            "It rose from 2.0 on 11 January 2023 to 3.0 on 12 January 2023. "
        )
        assert expected_text_about_plot_data in text

    def test_returns_correct_text_about_data_for_multiple_plots(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of 2 enriched `PlotData` models
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for each plot
        """
        # Given
        fake_plot_data.x_axis_values = [
            datetime.date(year=2023, month=1, day=i + 1)
            for i in range(len(fake_plot_data.y_axis_values))
        ]
        second_plot_data = fake_plot_data.model_copy(deep=True)
        second_plot_data.parameters.topic = "Influenza"
        second_plot_data.parameters.metric = "influenza_testing_positivityByWeek"
        second_plot_data.parameters.sex = "f"
        second_plot_data.parameters.age = "0_4"

        plots_text = PlotsText(plots_data=[fake_plot_data, second_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_plot_1_data_summary = (
            "This plot shows data from 01 January 2023 to 12 January 2023. "
            "It rose from 1.0 on 01 January 2023 to 2.0 on 02 January 2023. "
            "It rose from 4.0 on 03 January 2023 to 5.0 on 04 January 2023. "
            "It fell from 5.0 on 05 January 2023 to 2.0 on 06 January 2023. "
            "It rose from 1.0 on 07 January 2023 to 8.0 on 08 January 2023. "
            "It rose from 9.0 on 09 January 2023 to 10.0 on 10 January 2023. "
            "And finally. "
            "It rose from 2.0 on 11 January 2023 to 3.0 on 12 January 2023."
        )

        expected_plot_2_data_summary = (
            "This plot shows data from 01 January 2023 to 12 January 2023. "
            "It rose from 1.0 on 01 January 2023 to 2.0 on 02 January 2023. "
            "It rose from 4.0 on 03 January 2023 to 5.0 on 04 January 2023. "
            "It fell from 5.0 on 05 January 2023 to 2.0 on 06 January 2023. "
            "It rose from 1.0 on 07 January 2023 to 8.0 on 08 January 2023. "
            "It rose from 9.0 on 09 January 2023 to 10.0 on 10 January 2023. "
            "And finally. "
            "It rose from 2.0 on 11 January 2023 to 3.0 on 12 January 2023."
        )

        assert expected_plot_1_data_summary in text
        assert expected_plot_2_data_summary in text

    @mock.patch(f"{MODULE_PATH}.get_x_value_at_start_of_reporting_delay_period")
    def test_returns_correct_text_about_valid_reporting_delay_period(
        self,
        mocked_get_x_value_at_start_of_reporting_delay_period: mock.MagicMock,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given a list of 1 enriched `PlotData` model
            which will have an associated
            reporting delay period
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text provides commentary
            about the associated reporting delay period
        """
        # Given
        plots_text = PlotsText(plots_data=[fake_plot_data])
        fake_date = datetime.date(year=2024, month=7, day=19)
        mocked_get_x_value_at_start_of_reporting_delay_period.return_value = fake_date

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_reporting_delay_period = (
            "Data from 19 July 2024 onwards "
            "falls under the reporting delay period. "
            "This means those figures are still subject to retrospective updates "
            "and should therefore not be considered to be final. "
        )
        assert expected_text_about_reporting_delay_period in text

    @pytest.mark.parametrize(
        "error",
        [NoReportingDelayPeriodFoundError, ReportingDelayNotProvidedToPlotsError],
    )
    @mock.patch(f"{MODULE_PATH}.get_x_value_at_start_of_reporting_delay_period")
    def test_returns_correct_text_about_no_reporting_delay_period(
        self,
        mocked_get_x_value_at_start_of_reporting_delay_period: mock.MagicMock,
        error: Exception,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given a list of 1 enriched `PlotData` model
            which will not have an associated
            reporting delay period
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text provides commentary
            about having no reporting delay period
        """
        # Given
        plots_text = PlotsText(plots_data=[fake_plot_data])
        mocked_get_x_value_at_start_of_reporting_delay_period.side_effect = error

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_reporting_delay_period = "There is no reporting delay period being tracked for the data on this chart. "
        assert expected_text_about_reporting_delay_period in text

    def test_returns_correct_text_for_headline_data(
        self,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given a list of 1 enriched `PlotData` model
            which represents a headline data type
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text provides commentary
            about the single headline data plot
        """
        # Given
        fake_plot_data.parameters.metric = "COVID-19_headline_7DayAdmissions"
        fake_plot_data.parameters.chart_type = "bar"
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text = (
            f"This plot shows `{fake_plot_data.x_axis_values[0]}` along the X-axis. "
            f"And `{fake_plot_data.y_axis_values[0]}` along the Y-axis. "
        )
        assert expected_text in text

    def test_returns_correct_text_for_multiple_headline_data_types(
        self,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given a list of 2 enriched `PlotData` model
            which represents headline data types
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text provides commentary
            about the headline data plots
        """
        # Given
        fake_plot_data.parameters.metric = "COVID-19_headline_7DayOccupiedBeds"
        fake_plot_data.parameters.chart_type = "bar"

        second_plot_data = fake_plot_data.model_copy(deep=True)
        second_plot_data.parameters.topic = "Influenza"
        second_plot_data.parameters.metric = (
            "influenza_headline_ICUHDUadmissionRateLatest"
        )
        plots_text = PlotsText(plots_data=[fake_plot_data, second_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_for_plot_one = (
            f"This plot shows `{fake_plot_data.x_axis_values[0]}` along the X-axis. "
            f"And `{fake_plot_data.y_axis_values[0]}` along the Y-axis. "
        )
        assert expected_text_for_plot_one in text

        expected_text_for_plot_one = (
            f"This plot shows `{second_plot_data.x_axis_values[0]}` along the X-axis. "
            f"And `{second_plot_data.y_axis_values[0]}` along the Y-axis. "
        )
        assert expected_text_for_plot_one in text

    def test_can_describe_singular_timeseries_plots(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of 2 enriched `PlotData` models
            which represents singular time series
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text provides commentary
            about the singular metric values
        """
        # Given
        fake_plot_data.y_axis_values = [Decimal("123.0000")]
        fake_plot_data.x_axis_values = ["London"]

        second_plot_data = fake_plot_data.model_copy(deep=True)
        second_plot_data.y_axis_values = [Decimal("456.0100")]
        second_plot_data.x_axis_values = ["Leeds"]
        plots_text = PlotsText(plots_data=[fake_plot_data, second_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        assert "This plot has a value of '123'" in text
        assert "This plot has a value of '456.01'" in text

    def test_describe_singular_metric_value_returns_empty_string_for_timeseries_plots_with_no_data(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given an enriched `PlotData` model
            which represents multiple time series
        When `_describe_singular_metric_value()` is called
            from an instance of `PlotsText`
        Then an empty string is returned
        """
        # Given
        fake_plot_data.y_axis_values = [Decimal("123.0000"), Decimal("456.0100")]
        fake_plot_data.x_axis_values = ["London", "London"]

        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text._describe_singular_metric_value(plot_data=fake_plot_data)

        # Then
        assert text == ""
