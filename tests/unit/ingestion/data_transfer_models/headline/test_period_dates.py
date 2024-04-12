import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.headline import (
    InboundHeadlineSpecificFields,
)


class TestInboundHeadlineSpecificFieldsForPeriodDates:
    def test_period_end_after_period_start_is_deemed_valid(self):
        """
        Given a `period_end` which is after the `period_start`
        When the `InboundHeadlineSpecificFields` is initialized
        Then the model is deemed valid
        """
        # Given
        period_end = "2024-04-17"
        period_start = "2024-04-10"

        # When
        headline_model = InboundHeadlineSpecificFields(
            period_start=period_start,
            period_end=period_end,
            embargo=None,
            metric_value=123,
        )

        # Then
        headline_model.model_validate(obj=headline_model, strict=True)

    def test_period_end_as_same_date_as_period_start_is_deemed_valid(self):
        """
        Given a `period_end` which is the same date as the `period_start`
        When the `InboundHeadlineSpecificFields` is initialized
        Then the model is deemed valid
        """
        # Given
        period_end = "2024-04-10"
        period_start = "2024-04-10"

        # When
        headline_model = InboundHeadlineSpecificFields(
            period_start=period_start,
            period_end=period_end,
            embargo=None,
            metric_value=123,
        )

        # Then
        headline_model.model_validate(obj=headline_model, strict=True)

    def test_period_end_being_set_before_period_end_is_deemed_invalid(self):
        """
        Given a `period_end` which is before the `period_start`
        When the `InboundHeadlineSpecificFields` is initialized
        Then a `ValidationError` is raised
        """
        # Given
        period_end = "2024-04-10"
        period_start = "2024-04-12"

        # When
        with pytest.raises(ValidationError):
            InboundHeadlineSpecificFields(
                period_start=period_start,
                period_end=period_end,
                embargo=None,
                metric_value=123,
            )
