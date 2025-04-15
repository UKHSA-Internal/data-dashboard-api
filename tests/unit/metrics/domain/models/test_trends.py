import pytest
from pydantic import ValidationError

from metrics.domain.models.trends import TrendsParameters


class TestTrendParameters:
    valid_payload = {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayChange",
        "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
        "geography": "England",
        "geography_type": "Nation",
        "stratum": "default",
        "sex": "all",
        "age": "all",
    }

    @pytest.mark.parametrize(
        "field",
        [
            "stratum",
            "geography",
            "geography_type",
            "sex",
            "age",
            "topic",
            "metric",
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
