from metrics.domain.models import PlotData
from metrics.domain.models.plots_text import PlotsText
from metrics.domain.utils import ChartTypes


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
        self, fake_plot_data: PlotData
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
        self, fake_plot_data: PlotData
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
        fake_plot_data.parameters.chart_type = ChartTypes.line_with_shaded_section.value
        fake_plot_data.parameters.label = label
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text_about_parameters = (
            f"There is only 1 plot on this chart. "
            f"The horizontal X-axis is labelled 'metric'. "
            f"Whilst the vertical Y-axis is labelled 'date'. "
            f"The only plot on this chart is a blue solid line plot. "
            f"The plot has a label of '{label}'. "
            f"This plot shows data for COVID-19. "
            f"Specifically the metric 'COVID-19_deaths_ONSByDay' for the London area, "
            f"along with the age banding of 'all' for the gender group of all. "
        )
        assert expected_text_about_parameters in text

    def test_returns_correct_text_about_parameters_for_multiple_plots(
        self, fake_plot_data: PlotData
    ):
        """
        Given a list of 1 enriched `PlotData` model
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for the plot
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
            "Plot number 1 on this chart is a blue solid line plot. "
            "This plot shows data for COVID-19. "
            "Specifically the metric 'COVID-19_deaths_ONSByDay' for the London area, "
            "along with the age banding of 'all' for the gender group of all. "
        )
        expected_plot_2_params_description = (
            "Plot number 2 on this chart is a blue dash line plot. "
            "This plot shows data for Influenza. "
            "Specifically the metric 'influenza_testing_positivityByWeek' "
            "for the London area, "
            "along with the age banding of '0_4' for the gender group of females. "
        )
        expected_plot_3_params_description = (
            "Plot number 3 on this chart is a blue solid bar plot. "
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
