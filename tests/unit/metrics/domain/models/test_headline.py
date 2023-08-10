import pytest

from metrics.domain.models.headline import HeadlineParameters


class TestHeadlineParameters:
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
        metric = "COVID-19_headline_ONSdeaths_7daytotals"

        # When
        headline_parameters = HeadlineParameters(topic=topic, metric=metric)
        setattr(headline_parameters, optional_field, None)

        # Then
        property_to_get = f"{optional_field}_name"
        assert getattr(headline_parameters, property_to_get) == ""
