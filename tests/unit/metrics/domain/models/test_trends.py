import pytest
from pydantic import ValidationError

from metrics.domain.models.trends import TrendsParameters


class TestTrendParameters:
    valid_payload = {
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayChange",
        "geography": "England",
        "geography_type": "Nation",
        "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
        "stratum": "default",
        "sex": "all",
        "age": "all",
    }

    @pytest.mark.parametrize(
        "field",
        [
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography",
            "geography_type",
            "stratum",
            "sex",
            "age",
            "percentage_metric",
        ],
    )
    def test_mandatory_fields_are_required(self, field: str):
        """
        Given an otherwise valid payload
        And a mandatory field which is passed as None
        When the `TrendsParameters` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        input_data = self.valid_payload.copy()
        input_data.pop(field)

        # When / Then
        with pytest.raises(ValidationError):
            TrendsParameters(**input_data)

    def test_to_dict_for_main_metric_query(self):
        """
        Given an enriched `TrendsParameters` model
        When `to_dict_for_main_metric_query()` is called
        Then the correct dictionary is returned
        """
        # Given
        input_data = self.valid_payload.copy()
        trend_parameters = TrendsParameters(**input_data)

        # When
        main_metric_dict = trend_parameters.to_dict_for_main_metric_query()

        # Then
        expected = {
            "theme": input_data["theme"],
            "sub_theme": input_data["sub_theme"],
            "topic": input_data["topic"],
            "metric": input_data["metric"],
            "geography": input_data["geography"],
            "geography_type": input_data["geography_type"],
            "stratum": input_data["stratum"],
            "sex": input_data["sex"],
            "age": input_data["age"],
            "rbac_permissions": [],
        }
        assert main_metric_dict == expected

    def test_to_dict_for_percentage_metric_query(self):
        """
        Given an enriched `TrendsParameters` model
        When `to_dict_for_percentage_metric_query()` is called
        Then the correct dictionary is returned
        """
        # Given
        input_data = self.valid_payload.copy()
        trend_parameters = TrendsParameters(**input_data)

        # When
        percentage_metric_dict = trend_parameters.to_dict_for_percentage_metric_query()

        # Then
        expected = {
            "theme": input_data["theme"],
            "sub_theme": input_data["sub_theme"],
            "topic": input_data["topic"],
            "metric": input_data["percentage_metric"],
            "geography": input_data["geography"],
            "geography_type": input_data["geography_type"],
            "stratum": input_data["stratum"],
            "sex": input_data["sex"],
            "age": input_data["age"],
            "rbac_permissions": [],
        }
        assert percentage_metric_dict == expected
