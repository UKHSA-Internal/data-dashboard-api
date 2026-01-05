import datetime
from unittest import mock

import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.headline import (
    HeadlineDTO,
    InboundHeadlineSpecificFields,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE

VALID_DATETIME = "2023-11-20 12:00:00"
MODULE_PATH = "ingestion.data_transfer_models.headline"

SPECIFIC_FIELDS = [
    "period_start",
    "period_end",
    "embargo",
    "metric_value",
]


class TestInboundHeadlineSpecificFields:
    def test_casts_dates_for_period_start_and_end(self):
        """
        Given a payload containing a date strings
            for `period_start` & `period_end`
        When the `InboundHeadlineSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = "2023-11-27"

        # When
        inbound_headline_specific_fields_validation = InboundHeadlineSpecificFields(
            period_start=fake_period_start,
            period_end=fake_period_end,
            embargo=VALID_DATETIME,
            metric_value=123,
        )

        # Then
        inbound_headline_specific_fields_validation.model_validate(
            inbound_headline_specific_fields_validation,
            strict=True,
        )

    def test_validates_embargo_of_none(self):
        """
        Given a payload containing valid values
            which contains an `embargo` field of None
        When the `InboundHeadlineSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = "2023-11-27"
        fake_embargo = None

        # When
        inbound_headline_specific_fields_validation = InboundHeadlineSpecificFields(
            period_start=fake_period_start,
            period_end=fake_period_end,
            embargo=fake_embargo,
            metric_value=123,
        )

        # Then
        inbound_headline_specific_fields_validation.model_validate(
            inbound_headline_specific_fields_validation,
            strict=True,
        )

    def test_validates_datetime_passed_to_period_start(self):
        """
        Given a payload containing a datetime string for `period_start`
        When the `InboundHeadlineSpecificFields` model is initialized
        Then the model is deemed valid
        """
        # Given
        fake_period_start = VALID_DATETIME
        fake_period_end = "2023-11-27"

        # When
        inbound_headline_specific_fields_validation = InboundHeadlineSpecificFields(
            period_start=fake_period_start,
            period_end=fake_period_end,
            metric_value=123,
            embargo=None,
        )

        # Then
        inbound_headline_specific_fields_validation.model_validate(
            inbound_headline_specific_fields_validation,
            strict=True,
        )

    def test_validates_when_datetime_passed_to_period_end(self):
        """
        Given a payload containing a datetime string for `period_end`
        When the `InboundHeadlineSpecificFields` model is initialized
        Then the model is deemed valid
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = VALID_DATETIME

        # When
        inbound_headline_specific_fields_validation = InboundHeadlineSpecificFields(
            period_start=fake_period_start,
            period_end=fake_period_end,
            metric_value=123,
            embargo=None,
        )

        # Then
        inbound_headline_specific_fields_validation.model_validate(
            inbound_headline_specific_fields_validation,
            strict=True,
        )

    def test_validates_date_passed_to_embargo(self):
        """
        Given a payload containing a date string for `embargo`
            without a specified timestamp
        When the `InboundHeadlineSpecificFields` model is initialized
        Then the model is deemed valid
        And the embargo is cast on the correct date
            with a timestamp of midnight
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = "2023-11-27"
        fake_embargo = "2023-11-30"

        # When
        inbound_headline_specific_fields_validation = InboundHeadlineSpecificFields(
            period_start=fake_period_start,
            period_end=fake_period_end,
            embargo=fake_embargo,
            metric_value=123,
        )

        # Then
        inbound_headline_specific_fields_validation.model_validate(
            inbound_headline_specific_fields_validation,
            strict=True,
        )

        validated_embargo: datetime.datetime = (
            inbound_headline_specific_fields_validation.embargo
        )
        assert validated_embargo.year == 2023
        assert validated_embargo.month == 11
        assert validated_embargo.day == 30
        assert validated_embargo.hour == 0
        assert validated_embargo.minute == 0
        assert validated_embargo.second == 0

    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", False)
    def test_raises_error_when_non_public_data_passed_to_public_platform(self):
        """
        Given a payload with `is_public` set to False
        And `AUTH_ENABLED` is set to False
        When the `InboundHeadlineSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = "2023-11-27"
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            InboundHeadlineSpecificFields(
                period_start=fake_period_start,
                period_end=fake_period_end,
                embargo=fake_embargo,
                metric_value=123,
                is_public=False,
            )

    @pytest.mark.parametrize("is_public", [True, False])
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True)
    def test_validates_public_or_private_data_when_auth_enabled_is_true(
        self, is_public: bool
    ):
        """
        Given a payload containing `is_public` as True or False
        And `AUTH_ENABLED` is set to True
        When the `InboundHeadlineSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = VALID_DATETIME

        # When
        inbound_headline_specific_fields_validation = InboundHeadlineSpecificFields(
            period_start=fake_period_start,
            period_end=fake_period_end,
            metric_value=123,
            embargo=None,
            is_public=is_public,
        )

        # Then
        inbound_headline_specific_fields_validation.model_validate(
            inbound_headline_specific_fields_validation,
            strict=True,
        )


class TestHeadlineDTO:
    def test_casts_upper_and_lower_level_fields(
        self, example_headline_data: INCOMING_DATA_TYPE
    ):
        """
        Given valid incoming source data for a headline data type
        When the `InboundHeadlineSpecificFields` is initialized
            with a list of initialized `HeadlineDTO` models
        Then the payload is deemed valid
        """
        # Given
        source_data = example_headline_data

        # When
        lower_level_fields = [
            InboundHeadlineSpecificFields(**individual_source_data)
            for individual_source_data in source_data["data"]
        ]

        headline_dto = HeadlineDTO(
            parent_theme=source_data["parent_theme"],
            child_theme=source_data["child_theme"],
            topic=source_data["topic"],
            metric_group=source_data["metric_group"],
            metric=source_data["metric"],
            geography_type=source_data["geography_type"],
            geography=source_data["geography"],
            geography_code=source_data["geography_code"],
            age=source_data["age"],
            sex=source_data["sex"],
            stratum=source_data["stratum"],
            refresh_date=source_data["refresh_date"],
            data=lower_level_fields,
        )

        # Then
        headline_dto.model_validate(headline_dto)
