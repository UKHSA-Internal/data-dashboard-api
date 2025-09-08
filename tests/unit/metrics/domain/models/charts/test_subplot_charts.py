import copy

from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.api.views.tables.subplot_tables.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters


class TestSubplotChartRequestParameters:
    def test_output_payload_for_tables(self):
        """
        Given a valid payload for subplot tables
        When `output_payload_for_tables()` is called from
            an instance of `SubplotChartRequestParameters`
        Then the result is flipped into groups as defined by the `x_axis`
            into a list of `PlotParamters` models which can be given
            to the `TablesInterface`
        """
        # Given
        payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: SubplotChartRequestParameters = serializer.to_models(request=None)

        # When
        output: list[ChartRequestParams] = params.output_payload_for_tables()

        # Then
        # Since the `x_axis` was set to "geography"
        # We expect England, North East, Darlington to dictate the resulting groups
        assert len(output) == 3

        expected_plot_parameters = [
            ("6-in-1", "6-in-1_coverage_coverageByYear", "6-in-1 (12 months)", "12m"),
            ("6-in-1", "6-in-1_coverage_coverageByYear", "6-in-1 (24 months)", "24m"),
            ("MMR1", "MMR1_coverage_coverageByYear", "MMR1 (24 months)", "24m"),
            ("MMR1", "MMR1_coverage_coverageByYear", "MMR1 (5 years)", "5y"),
        ]

        for subplot in output:
            # Each subplot will hold 4 plots. 1 for each topic/metric/stratum combination
            assert len(subplot.plots) == 4
            for index, (topic, metric, label, stratum) in enumerate(
                expected_plot_parameters
            ):
                plot = subplot.plots[index]
                assert plot.topic == topic
                assert plot.metric == metric
                assert plot.label == label
                assert plot.stratum == stratum
                # `age` and `sex` are pinned to "all" across the board
                assert plot.age == "all"
                assert plot.sex == "all"

        geographies = [
            ("England", "Nation"),
            ("North East", "Region"),
            ("Darlington", "Upper Tier Local Authority"),
        ]

        for index, (geography, geography_type) in enumerate(geographies):
            subplot = output[index]
            assert subplot.x_axis == "geography"
            assert subplot.y_axis == "metric"
            # All the plots within each subplot should be set to the
            # geography specific to that subplot
            for plot in subplot.plots:
                assert plot.geography == geography
                assert plot.geography_type == geography_type

    def test_output_payload_for_tables_handles_missing_plot_in_subplot(self):
        """
        Given a payload where one subplot is missing a plot
            for a particular geography
        When `output_payload_for_tables()` is called from
            an instance of `SubplotChartRequestParameters`
        Then the corresponding output `ChartRequestParams`
            model omits the missing plot
        """
        # Given
        payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
        # Remove the England plot from the 3rd subplot (MMR1 24 months)
        # so for there is no matching plot for "England" in that subplot
        third_subplot = payload["subplots"][2]
        third_subplot["plots"] = [
            plot for plot in third_subplot["plots"] if plot["geography"] != "England"
        ]

        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: SubplotChartRequestParameters = serializer.to_models(request=None)

        # When
        output: list[ChartRequestParams] = params.output_payload_for_tables()

        # Then
        # We still expect 3 groups i.e. England, North East, Darlington
        assert len(output) == 3

        england_group = output[0]
        # Originally there were 4 plots in each subplot
        # But for the "England" subplot there will now only be 3 plots
        assert len(england_group.plots) == 3
        expected_labels_for_england_subplot = [
            "6-in-1 (12 months)",
            "6-in-1 (24 months)",
            # "MMR1 (24 months)" is missing for England in this case
            "MMR1 (5 years)",
        ]
        assert [
            plot.label for plot in england_group.plots
        ] == expected_labels_for_england_subplot

        # The other groups (North East & Darlington) still have all 4 plots
        assert len(output[1].plots) == 4
        assert len(output[2].plots) == 4
