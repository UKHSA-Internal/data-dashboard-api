import pytest
from pydantic import ValidationError

from metrics.domain.models.trends import TrendsParameters


class TestTrendParameters:
    @pytest.mark.parametrize(
        "mandatory_field",
        [
            "topic",
            "metric",
            "percentage_metric",
        ],
    )
    def test_mandatory_fields_are_required(self, mandatory_field: str):
        """
        Given an otherwise valid payload
        And a mandatory field which is passed as None
        When the `TrendsParameters` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = {
            "topic": "COVID-19",
            "metric": "COVID-19_headline_ONSdeaths_7DayChange",
            "percentage_metric": "COVID-19_headline_ONSdeaths_7daypercentchange",
        }
        payload[mandatory_field] = None

        # When / Then
        with pytest.raises(ValidationError):
            TrendsParameters(**payload)

    @pytest.mark.parametrize(
        "optional_field",
        [
            "stratum",
            "geography",
            "geography_type",
            "sex",
            "age",
        ],
    )
    def test_optional_fields_default_to_empty_string(self, optional_field: str):
        """
        Given a valid topic and metric
        And an optional field which has been passed as None
        When the `HeadlineParameters` model is initialized
        Then an empty string is returned for the optional field
        """
        # Given
        topic = "COVID-19"
        metric = "COVID-19_headline_ONSdeaths_7DayChange"
        percentage_metric = "COVID-19_headline_ONSdeaths_7daypercentchange"

        # When
        headline_parameters = TrendsParameters(
            topic=topic, metric=metric, percentage_metric=percentage_metric
        )
        setattr(headline_parameters, optional_field, None)

        # Then
        property_to_get = f"{optional_field}_name"
        assert getattr(headline_parameters, property_to_get) == ""
