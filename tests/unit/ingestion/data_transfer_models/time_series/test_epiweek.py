import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.time_series import InboundTimeSeriesSpecificFields


class TestInboundTimeSeriesSpecificFieldsForEpiWeek:
    @property
    def payload_without_epiweek(self) -> dict[str, str | int | None]:
        return {
            "date": "2023-11-01",
            "embargo": None,
            "metric_value": 123,
            "is_public": True,
        }

    @pytest.mark.parametrize("epiweek", list(range(1, 53 + 1)))
    def test_epiweek_between_1_and_53_is_valid(self, epiweek: int):
        """
        Given an epiweek between 1 and 53
        When the `InboundTimeSeriesSpecificFields` is initialized
        Then the model is deemed valid
        """
        # Given
        payload = self.payload_without_epiweek
        payload["epiweek"] = epiweek

        # When
        time_series_model = InboundTimeSeriesSpecificFields(**payload)

        # Then
        time_series_model.model_validate(obj=time_series_model, strict=True)

    @pytest.mark.parametrize("epiweek", [54, 55, 100])
    def test_epiweek_greater_than_53_is_deemed_invalid(self, epiweek: int):
        """
        Given an epiweek greater than 53
        When the `InboundTimeSeriesSpecificFields` is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = self.payload_without_epiweek
        payload["epiweek"] = epiweek

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(**payload)

    def test_epiweek_of_0_is_deemed_invalid(self):
        """
        Given an epiweek of 0
        When the `InboundTimeSeriesSpecificFields` is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = self.payload_without_epiweek
        payload["epiweek"] = 0

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(**payload)
