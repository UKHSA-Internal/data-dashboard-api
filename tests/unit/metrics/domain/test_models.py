from typing import Dict

from metrics.domain.models import ChartPlotParameters


class TestChartPlotParameters:
    def test_to_dict_for_query(self, fake_chart_plot_parameters: ChartPlotParameters):
        """
        Given a payload containing optional fields which do not relate
            directly to the corresponding query filters
        When `to_dict_for_query()` is called from an instance of the `ChartPlotParameters` model
        Then the returned dict contains the expected key-value pairs only
        """
        # Given
        geography = "London"
        geography_type = "Nation"
        date_from = "2022-10-01"
        label = "0 to 4 years old"

        fake_chart_plot_parameters.geography = geography
        fake_chart_plot_parameters.geography_type = geography_type
        fake_chart_plot_parameters.date_from = date_from
        fake_chart_plot_parameters.label = label

        # When
        dict_used_for_query: Dict[
            str, str
        ] = fake_chart_plot_parameters.to_dict_for_query()

        # Then
        expected_dict_used_for_query = {
            "topic": fake_chart_plot_parameters.topic,
            "metric": fake_chart_plot_parameters.metric,
            "stratum": fake_chart_plot_parameters.stratum,
            "geography": fake_chart_plot_parameters.geography,
            "geography_type": fake_chart_plot_parameters.geography_type,
        }
        # `chart_type`, `label` and `date_from`are omitted
        assert dict_used_for_query == expected_dict_used_for_query
