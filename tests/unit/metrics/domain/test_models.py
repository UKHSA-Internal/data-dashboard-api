from typing import Dict, Optional

import pytest

from metrics.domain.models import ChartPlotParameters


class TestChartPlotParameters:
    mandatory_parameters = {
        "chart_type": "bar",
        "topic": "COVID-19",
        "metric": "new_cases_daily",
    }
    optional_field_names = [
        "stratum",
        "geography",
        "geography_type",
        "date_from",
        "date_to",
        "label",
        "line_colour",
        "line_type",
    ]

    def test_validates_successfully_when_optional_parameters_are_none(self):
        """
        Given a set of mandatory parameters and None for each optional field
        When an instance of the `ChartPlotParameters` model is created
        Then a `ValidationError` is not raised
        """
        # Given
        optional_parameters_as_none = {
            field_name: None for field_name in self.optional_field_names
        }

        # When / Then
        ChartPlotParameters(**self.mandatory_parameters, **optional_parameters_as_none)

    def test_validates_successfully_when_optional_parameters_are_empty_strings(self):
        """
        Given a set of mandatory parameters and an empty string for each optional field
        When an instance of the `ChartPlotParameters` model is created
        Then a `ValidationError` is not raised
        """
        # Given
        optional_parameters_as_empty_strings = {
            field_name: "" for field_name in self.optional_field_names
        }

        # When / Then
        ChartPlotParameters(
            **self.mandatory_parameters, **optional_parameters_as_empty_strings
        )

    def test_validates_successfully_when_optional_parameters_not_provided(self):
        """
        Given a set of mandatory parameters and no optional fields provided
        When an instance of the `ChartPlotParameters` model is created
        Then a `ValidationError` is not raised
        """
        # Given
        optional_parameters = {}

        # When / Then
        ChartPlotParameters(**self.mandatory_parameters, **optional_parameters)

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
        line_colour = "BLUE"
        line_type = "dash"

        fake_chart_plot_parameters.geography = geography
        fake_chart_plot_parameters.geography_type = geography_type
        fake_chart_plot_parameters.date_from = date_from
        fake_chart_plot_parameters.label = label
        fake_chart_plot_parameters.line_colour = line_colour
        fake_chart_plot_parameters.line_type = line_type

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
        # `chart_type`, `label`, `line_colour`, `line_type`, `date_to` and `date_from` are omitted
        assert dict_used_for_query == expected_dict_used_for_query
