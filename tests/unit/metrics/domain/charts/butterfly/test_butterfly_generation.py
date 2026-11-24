import random

import pytest

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

    @pytest.mark.parametrize(
        "y_axis_data, x_axis_data, expected_tick_vals",
        [
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0, 1000, 2000, 3000, 4000, 5000],
                [0, 1000, 2000, 3000, 4000, 5000],
                id="thousands",
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0, 100, 200, 300, 400, 500],
                [0, 100, 200, 300, 400, 500],
                id="hundreds",
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0, 50, 100, 150, 200, 250],
                [0, 50, 100, 150, 200, 250],
                id="fiftys",
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0, 40, 80, 120, 160, 200],
                [0, 50, 100, 150, 200, 250],
                id="forties",
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0, 20, 40, 60, 80, 100],
                [0, 20, 40, 60, 80, 100],
                id="twentys",
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0, 10, 20, 30, 40, 50],
                [0, 10, 20, 30, 40, 50],
                id="tens",
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5], [0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8, 10], id="twos"
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], id="ones"
            ),
            pytest.param(
                [0, 1, 2, 3, 4, 5],
                [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                [0, 0.1, 0.2, 0.3, 0.4, 0.5],
                id="tenths",
            ),
        ],
    )
    def test_generated_tickmarks(
        self,
        y_axis_data,
        x_axis_data,
        expected_tick_vals,
    ):

        plots = self.generate_plots(
            self,
            y_axis_data=y_axis_data,
            left_side=x_axis_data,
            right_side=x_axis_data,
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

        tickvals = list(
            generate_butterfly(chart_generation_payload=chart_payload).layout["xaxis"][
                "tickvals"
            ]
        )
        ticktext = list(
            generate_butterfly(chart_generation_payload=chart_payload).layout["xaxis"][
                "ticktext"
            ]
        )

        expected_full_range_tick_vals = self.mirror_array(expected_tick_vals)
        expected_full_range_tick_text = self.format_axis_labels(
            expected_full_range_tick_vals
        )
        assert tickvals == expected_full_range_tick_vals
        assert expected_full_range_tick_text == ticktext

    @staticmethod
    def generate_plots(
        self,
        y_axis_data: list,
        left_side: list,
        right_side: list,
    ):

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
        for i in range(y_axis_data.__len__()):
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
        return plots

    @staticmethod
    def mirror_array(arr):
        arr_list = list(arr)
        negatives = [-x for x in reversed(arr_list) if x != 0]
        return negatives + arr_list

    @staticmethod
    def format_axis_labels(numbers):
        formatted = []
        for x in numbers:
            # Round to 1 decimal place first to avoid '.0' after rounding (e.g. 1.99 -> 2.0)
            rounded = round(abs(float(x)), 1)
            if rounded.is_integer():
                formatted.append(f"{rounded:,.0f}")
            else:
                formatted.append(f"{rounded:,.1f}")
        return formatted
