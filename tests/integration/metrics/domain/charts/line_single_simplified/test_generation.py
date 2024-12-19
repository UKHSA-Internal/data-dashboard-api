import datetime
from unittest import mock

import plotly.graph_objects

from metrics.domain.charts.colour_scheme import RGBAColours
from metrics.domain.charts.line_single_simplified import generation
from metrics.domain.models import PlotGenerationData

DATES_FROM_SEP_TO_JAN: list[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2023, 1, 9),
]


class TestLineSingleSimplified:
    def test_line_single_simplified_figure_is_drawn_with_expected_params(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of dates and values
        When `generate_chart_figure()` is called from the `line_single_simplified` module
        Then the figure is drawn with the expected parameters
        """
        # Given
        fake_plot_data.x_axis_values = DATES_FROM_SEP_TO_JAN
        fake_plot_data.y_axis_values = [1.1, 0.9, 0.8, 0.3]
        chart_height = 200
        chart_width = 400

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            plot_data=[fake_plot_data],
            chart_height=chart_height,
            chart_width=chart_width,
        )

        # Then
        main_layout = figure.layout
        assert main_layout.paper_bgcolor == RGBAColours.WHITE.stringified
        assert not main_layout.showlegend
        assert main_layout.height == chart_height
        assert main_layout.width == chart_width

        assert figure.layout.margin.l == 25
        assert figure.layout.margin.r == 35
        assert figure.layout.margin.pad == 25

        assert figure.layout.xaxis.tickvals == (
            fake_plot_data.x_axis_values[0],
            fake_plot_data.x_axis_values[-1],
        )
        assert figure.layout.xaxis.ticktext == (
            fake_plot_data.x_axis_values[0].strftime("%b, %Y"),
            fake_plot_data.x_axis_values[-1].strftime("%b, %Y"),
        )

        assert figure.layout.yaxis.tickvals == (0, max(fake_plot_data.y_axis_values))
        assert figure.layout.yaxis.ticktext == (
            "0",
            "1",
        )
