from metrics.domain.models import PlotData
from metrics.domain.models.plots_text import PlotsText


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

    def test_returns_correct_text_for_one_plot(self, fake_plot_data: PlotData):
        """
        Given a list of 1 enriched `PlotData` model
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for the plot
        """
        # Given
        plots_text = PlotsText(plots_data=[fake_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text = (
            "There is only 1 plot on this chart. "
            "The horizontal X-axis is labelled 'metric'. "
            "Whilst the vertical Y-axis is labelled 'date'. "
            "The only plot on this chart is a blue solid line plot. "
            "This plot shows data for COVID-19. "
            "Specifically the metric 'COVID-19_deaths_ONSByDay' for the London area, "
            "along with the age banding of 'all' for the gender group of all. "
        )
        assert text == expected_text

    def test_returns_correct_text_for_multiple_plots(self, fake_plot_data: PlotData):
        """
        Given a list of 1 enriched `PlotData` model
        When `construct_text()` is called
            from an instance of `PlotsText`
        Then the returned text declares the parameters
            which were used for the plot
        """
        # Given
        second_plot_data = fake_plot_data.copy()
        second_plot_data.parameters.topic = "Influenza"
        second_plot_data.parameters.metric = "influenza_testing_positivityByWeek"
        second_plot_data.parameters.sex = "f"
        second_plot_data.parameters.age = "0_4"
        second_plot_data.parameters.line_type = "DASH"
        plots_text = PlotsText(plots_data=[fake_plot_data, second_plot_data])

        # When
        text: str = plots_text.construct_text()

        # Then
        expected_text = (
            "There are 2 plots on this chart. "
            "The horizontal X-axis is labelled 'metric'. "
            "Whilst the vertical Y-axis is labelled 'date'. "
            "Plot number 1 on this chart is a blue dash line plot. "
            "This plot shows data for Influenza. "
            "Specifically the metric 'influenza_testing_positivityByWeek' for the London area, "
            "along with the age banding of '0_4' for the gender group of females. "
            "Plot number 2 on this chart is a blue dash line plot. "
            "This plot shows data for Influenza. "
            "Specifically the metric 'influenza_testing_positivityByWeek' for the London area,"
            " along with the age banding of '0_4' for the gender group of females. "
        )

        assert text == expected_text
