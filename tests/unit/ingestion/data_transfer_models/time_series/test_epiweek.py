import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.time_series import InboundTimeSeriesSpecificFields


class TestInboundTimeSeriesSpecificFieldsForEpiWeek:
    @property
    def payload_without_epiweek_or_date(self) -> dict[str, int | None]:
        return {
            "embargo": None,
            "metric_value": 123,
        }

    @pytest.mark.parametrize(
        "input_epiweek, input_date",
        (
            [44, "2022-11-01"],
            [45, "2022-11-09"],
            [46, "2022-11-18"],
            [46, "2022-11-20"],
            [49, "2022-12-09"],
            [50, "2022-12-14"],
            [52, "2022-12-31"],
            [52, "2023-01-01"],
            [1, "2023-01-02"],
            [2, "2023-01-09"],
        ),
    )
    def test_epiweek_between_1_and_53_is_valid(
        self, input_epiweek: int, input_date: str
    ):
        """
        Given an epiweek between 1 and 53
        When the `InboundTimeSeriesSpecificFields` is initialized
        Then the model is deemed valid
        """
        # Given
        payload = self.payload_without_epiweek_or_date
        payload["epiweek"] = input_epiweek
        payload["date"] = input_date

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
        payload = self.payload_without_epiweek_or_date
        payload["epiweek"] = epiweek
        payload["date"] = "2023-12-31"

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
        payload = self.payload_without_epiweek_or_date
        payload["epiweek"] = 0
        payload["date"] = "2024-01-01"

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(**payload)
