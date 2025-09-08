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
