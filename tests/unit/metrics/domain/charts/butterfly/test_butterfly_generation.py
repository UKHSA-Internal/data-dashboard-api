import random

from metrics.domain.charts.butterfly.generation import generate_butterfly
from metrics.domain.models import (
    ChartGenerationPayload,
    PlotGenerationData,
    PlotParameters,
)

HEIGHT = 400
WIDTH = 640


class TestGenerateButterfly:

    def test_generate_butterfly_chart(self):

        # generate a random total set of random numbers for y axis in order
        random_count = random.randint(20, 100)
        y_axis_data = sorted(random.sample(range(0, 100), random_count))
        # Two arrays of random numbers for the x-axis
        left_side = random.sample(range(0, 100), random_count)
        right_side = random.sample(range(0, 100), random_count)

        plots = []
        left_label = "Left"
        left_plot_params = PlotParameters(
            chart_type="butterfly",
            topic="test",
            metric="headline_test",
            geography="test",
            geography_type="test",
            label=left_label,
            sex="m",
            line_colour="BLUE",
        )
        right_label = "Right"
        right_plot_params = PlotParameters(
            chart_type="butterfly",
            topic="test",
            metric="headline_test",
            geography="test",
            geography_type="test",
            label=right_label,
            sex="f",
            line_colour="RED",
        )
        for i in range(random_count):
            plots.append(
                PlotGenerationData(
                    parameters=left_plot_params,
                    y_axis_values=[y_axis_data[i]],
                    x_axis_values=[left_side[i]],
                )
            )
            plots.append(
                PlotGenerationData(
                    parameters=right_plot_params,
                    y_axis_values=[y_axis_data[i]],
                    x_axis_values=[right_side[i]],
                )
            )

        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=plots,
            x_axis_title="Cases",
            y_axis_title="Age",
            secondary_category="sex",
        )

        figure = generate_butterfly(chart_generation_payload=chart_payload)

        assert len(figure.data) == 2

        # left side data is negative in the graph
        assert list(figure.data[0].x) == [-x for x in left_side]
        assert list(figure.data[0].y) == y_axis_data
        assert len(figure.data[0].x) == random_count
        assert len(figure.data[0].y) == random_count

        assert list(figure.data[1].x) == right_side
        assert list(figure.data[1].y) == y_axis_data
        assert len(figure.data[1].x) == random_count
        assert len(figure.data[1].y) == random_count

        assert figure.data[0].name == left_label
        assert figure.data[1].name == right_label

        assert figure.data[0].orientation == "h"
        assert figure.data[1].orientation == "h"

        assert figure.data[0].marker.color == "rgba(29, 112, 184, 1)"
        assert figure.data[1].marker.color == "rgba(212, 53, 28, 1)"
