import numpy as np
import plotly.graph_objects

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.waffle import generation


class TestWaffleCharts:
    def test_plot_background(self):
        """
        Given a list of 1 threshold integer
        When `generate_chart_figure()` is called from the `waffle` module
        Then the figure is drawn with the expected parameters for the main layout frame
        """
        # Given
        plot_threshold_value = 86
        points: list[int] = [plot_threshold_value]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            values=points
        )

        # Then
        assert len(figure.data) == 1
        main_layout: plotly.graph_objects.Layout = figure.layout

        # Check the correct colours have been used for the paper and plot background colours
        assert (
            main_layout.paper_bgcolor
            == colour_scheme.RGBAColours.WAFFLE_WHITE.stringified
        )
        assert (
            main_layout.plot_bgcolor == colour_scheme.RGBAColours.LIGHT_GREY.stringified
        )

        # Check that the bottom, left, right and top margins are all equal to 0
        assert (
            main_layout.margin.b
            == main_layout.margin.l
            == main_layout.margin.r
            == main_layout.margin.t
            == 0
        )

    def test_plot_with_one_point(self):
        """
        Given a list of 1 threshold integer
        When `generate_chart_figure()` is called from the `waffle` module
        Then the figure is drawn with the expected parameters for the single plot
        """
        # Given
        plot_threshold_value = 86
        points: list[int] = [plot_threshold_value]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            values=points
        )

        # Then
        assert len(figure.data) == 1

        # ---Single plot checks---
        single_plot: plotly.graph_objects.Heatmap = figure.data[0]
        # Check that a heatmap has been drawn with the correct gaps in the x and y direction between cells
        assert single_plot.type == "heatmap"
        assert single_plot.xgap == single_plot.ygap == 3

        # There are no nan values so check that the sum of the `z` array is equal to the threshold value
        larger_plot_z_array: np.ndarray = single_plot.z
        assert int(larger_plot_z_array.sum()) == plot_threshold_value

    def test_plot_with_two_points(self):
        """
        Given a list of 2 threshold integers in decreasing order from largest to smallest
        When `generate_chart_figure()` is called from the `waffle` module
        Then the figure is drawn with the expected parameters for the 2 plots
        """
        # Given
        larger_plot_threshold_value = 86
        smaller_plot_threshold_value = 23
        points: list[int] = [larger_plot_threshold_value, smaller_plot_threshold_value]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            values=points
        )

        # Then
        assert len(figure.data) == 2

        # ---Larger plot checks---
        larger_plot: plotly.graph_objects.Heatmap = figure.data[0]
        # Check that a heatmap has been drawn with the correct gaps in the x and y direction between cells
        assert larger_plot.type == "heatmap"
        assert larger_plot.xgap == larger_plot.ygap == 3

        # There are no nan values so check that the sum of the `z` array is equal to the threshold value
        larger_plot_z_array: np.ndarray = larger_plot.z
        assert int(larger_plot_z_array.sum()) == larger_plot_threshold_value

        # ---Smaller plot checks---
        smaller_plot: plotly.graph_objects.Heatmap = figure.data[1]
        # Check that a heatmap has been drawn with the correct gaps in the x and y direction between cells
        assert smaller_plot.type == "heatmap"
        assert smaller_plot.xgap == smaller_plot.ygap == 3

        # Since there are nan values in the `z` array, slice either side of the threshold value
        smaller_plot_z_array: np.ndarray = smaller_plot.z
        smaller_plot_flattened_matrix = smaller_plot_z_array.flatten()

        # Check that the identifier is used for the first 23 items in the array
        for threshold_value in smaller_plot_flattened_matrix[
            :smaller_plot_threshold_value
        ]:
            assert threshold_value == 2.0

        # Check that the nan placeholder value is used for the remaining 77 items in the array
        for nan_value in smaller_plot_flattened_matrix[smaller_plot_threshold_value:]:
            np.isnan(nan_value)

    def test_plot_with_three_points(self):
        """
        Given a list of 3 threshold integers in decreasing order from largest to smallest
        When `generate_chart_figure()` is called from the `waffle` module
        Then the figure is drawn with the expected parameters for the 3 plots
        """
        # Given
        larger_plot_threshold_value = 86
        middle_plot_threshold_value = 41
        smaller_plot_threshold_value = 23
        values: list[int] = [
            larger_plot_threshold_value,
            middle_plot_threshold_value,
            smaller_plot_threshold_value,
        ]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            values=values
        )

        # ---Larger plot checks---
        larger_plot: plotly.graph_objects.Heatmap = figure.data[0]
        # Check that a heatmap has been drawn with the correct gaps in the x and y direction between cells
        assert larger_plot.type == "heatmap"
        assert larger_plot.xgap == larger_plot.ygap == 3

        # There are no nan values so check that the sum of the `z` array is equal to the threshold value
        larger_plot_z_array: np.ndarray = larger_plot.z
        assert int(larger_plot_z_array.sum()) == larger_plot_threshold_value

        # ---Middle plot checks---
        middle_plot: plotly.graph_objects.Heatmap = figure.data[1]
        # Check that a heatmap has been drawn with the correct gaps in the x and y direction between cells
        assert middle_plot.type == "heatmap"
        assert middle_plot.xgap == middle_plot.ygap == 3

        # Since there are nan values in the `z` array, slice either side of the threshold value
        middle_plot_z_array: np.ndarray = middle_plot.z
        middle_plot_flattened_matrix = middle_plot_z_array.flatten()

        # Check that the identifier is used for the first 23 items in the array
        for threshold_value in middle_plot_flattened_matrix[
            :middle_plot_threshold_value
        ]:
            assert threshold_value == 2.0

        # Check that the nan placeholder value is used for the remaining 77 items in the array
        for nan_value in middle_plot_flattened_matrix[middle_plot_threshold_value:]:
            np.isnan(nan_value)

        # ---Smaller plot checks---
        smaller_plot: plotly.graph_objects.Heatmap = figure.data[2]
        # Check that a heatmap has been drawn with the correct gaps in the x and y direction between cells
        assert smaller_plot.type == "heatmap"
        assert smaller_plot.xgap == smaller_plot.ygap == 3

        # Since there are nan values in the `z` array, slice either side of the threshold value
        smaller_plot_z_array: np.ndarray = smaller_plot.z
        smaller_plot_flattened_matrix = smaller_plot_z_array.flatten()

        # Check that the identifier is used for the first 23 items in the array
        for threshold_value in smaller_plot_flattened_matrix[
            :smaller_plot_threshold_value
        ]:
            assert threshold_value == 3.0

        # Check that the nan placeholder value is used for the remaining 77 items in the array
        for nan_value in smaller_plot_flattened_matrix[smaller_plot_threshold_value:]:
            np.isnan(nan_value)
