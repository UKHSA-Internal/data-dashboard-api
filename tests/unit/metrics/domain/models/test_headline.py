import pytest
from pydantic_core import ValidationError

from metrics.domain.models.headline import HeadlineParameters


class TestHeadlineParameters:
    valid_payload = {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
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
        ],
    )
    def test_mandatory_fields_are_enforced(self, field: str):
        """
        Given an otherwise valid payload
        And a mandatory field which has been omitted
        When the `HeadlineParameters` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        input_data = self.valid_payload.copy()
        input_data.pop(field)

        # When / Then
        with pytest.raises(ValidationError):
            HeadlineParameters(**input_data)
