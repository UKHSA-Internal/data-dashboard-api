from unittest import mock

import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.time_series import (
    InboundTimeSeriesSpecificFields,
    TimeSeriesDTO,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from metrics.data.enums import TimePeriod

VALID_DATETIME = "2023-11-20 12:00:00"
MODULE_PATH = "ingestion.data_transfer_models.time_series"


class TestInboundTimeSeriesSpecificFields:
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", False)
    def test_validates_payload(self):
        """
        Given a payload containing valid values
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_epiweek = 46
        fake_date = "2023-11-01"
        fake_embargo = VALID_DATETIME
        fake_metric_value = 123
        fake_force_write_value = True

        # When
        inbound_time_series_specific_fields_validation = (
            InboundTimeSeriesSpecificFields(
                epiweek=fake_epiweek,
                date=fake_date,
                embargo=fake_embargo,
                metric_value=fake_metric_value,
                force_write=fake_force_write_value,
                is_public=True,
            )
        )

        # Then
        inbound_time_series_specific_fields_validation.model_validate(
            inbound_time_series_specific_fields_validation,
            strict=True,
        )

    def test_validates_payload_with_embargo_of_none(self):
        """
        Given a payload containing valid values
            which contains an `embargo` field of None
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_epiweek = 46
        fake_date = "2023-11-01"
        fake_embargo = None
        fake_metric_value = 123

        # When
        imbound_time_series_specific_fields_validation = (
            InboundTimeSeriesSpecificFields(
                epiweek=fake_epiweek,
                date=fake_date,
                embargo=fake_embargo,
                metric_value=fake_metric_value,
                is_public=True,
            )
        )

        # Then
        imbound_time_series_specific_fields_validation.model_validate(
            imbound_time_series_specific_fields_validation,
            strict=True,
        )

    def test_raises_error_when_datetime_passed_to_epiweek(self):
        """
        Given a payload containing a datetime string for `epiweek`
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_epiweek = VALID_DATETIME
        fake_date = "2023-11-27"

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(
                epiweek=fake_epiweek,
                date=fake_date,
                embargo=VALID_DATETIME,
                metric_value=123,
            )

    def test_raises_error_when_datetime_passed_to_period_end(self):
        """
        Given a payload containing a datetime string for `date`
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_date = VALID_DATETIME
        fake_epiweek = 46
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(
                date=fake_date,
                epiweek=fake_epiweek,
                embargo=fake_embargo,
                metric_value=123,
            )

    def test_raises_error_when_date_passed_to_embargo(self):
        """
        Given a payload containing a date string for `embargo`
            without a specified timestamp
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then the model is deemed valid
        And the embargo is cast on the correct date
            with a timestamp of midnight
        """
        # Given
        fake_date = "2023-11-20"
        fake_epiweek = 46
        fake_embargo = "2023-11-30"

        # When
        inbound_time_series_specific_fields_validation = (
            InboundTimeSeriesSpecificFields(
                date=fake_date,
                epiweek=fake_epiweek,
                embargo=fake_embargo,
                metric_value=123,
                is_public=True,
            )
        )

        # Then
        validated_embargo = inbound_time_series_specific_fields_validation.embargo
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
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(
                epiweek=1,
                date="2023-11-20",
                embargo=VALID_DATETIME,
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
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_embargo = VALID_DATETIME
        fake_metric_value = 123

        # When
        inbound_time_series_specific_fields_validation = (
            InboundTimeSeriesSpecificFields(
                epiweek=46,
                date="2023-11-01",
                embargo=fake_embargo,
                metric_value=fake_metric_value,
                is_public=is_public,
            )
        )

        # Then
        inbound_time_series_specific_fields_validation.model_validate(
            inbound_time_series_specific_fields_validation,
            strict=True,
        )


class TestTimeSeriesDTO:
    def test_casts_upper_and_lower_level_fields(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given valid incoming source data for a headline data type
        When the `TimeSeriesDTO` is initialized with a list of
            initialized `InboundTimeSeriesSpecificFields` models
        Then the payload is deemed valid
        """
        # Given
        source_data = example_time_series_data

        # When
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        time_series_dto = TimeSeriesDTO(
            parent_theme=source_data["parent_theme"],
            child_theme=source_data["child_theme"],
            topic=source_data["topic"],
            metric_group=source_data["metric_group"],
            metric=source_data["metric"],
            metric_frequency=source_data["metric_frequency"],
            geography_type=source_data["geography_type"],
            geography=source_data["geography"],
            geography_code=source_data["geography_code"],
            age=source_data["age"],
            sex=source_data["sex"],
            stratum=source_data["stratum"],
            refresh_date=source_data["refresh_date"],
            time_series=lower_level_fields,
        )

        # Then
        time_series_dto.model_validate(time_series_dto)

    @pytest.mark.parametrize(
        "input_metric_frequency_value, expected_metric_frequency_value",
        [
            ("daily", TimePeriod.Daily.value),
            ("Daily", TimePeriod.Daily.value),
            ("weekly", TimePeriod.Weekly.value),
            ("Weekly", TimePeriod.Weekly.value),
            ("fortnightly", TimePeriod.Fortnightly.value),
            ("Fortnightly", TimePeriod.Fortnightly.value),
            ("monthly", TimePeriod.Monthly.value),
            ("Monthly", TimePeriod.Monthly.value),
            ("quarterly", TimePeriod.Quarterly.value),
            ("Quarterly", TimePeriod.Quarterly.value),
            ("annual", TimePeriod.Annual.value),
            ("Annual", TimePeriod.Annual.value),
        ],
    )
    def test_valid_payload_with_metric_frequency_is_cast_to_correct_output(
        self,
        input_metric_frequency_value: str,
        expected_metric_frequency_value: str,
        example_time_series_data: INCOMING_DATA_TYPE,
    ):
        """
        Given a payload containing valid values
            which contains a `sex` value of "Male"
        When the `TimeSeriesDTO` model is initialized
        Then model is deemed valid
        And the correct value is cast for the output "metric_frequency" field
        """
        # Given
        source_data = example_time_series_data

        # When
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        time_series_dto = TimeSeriesDTO(
            metric_frequency=input_metric_frequency_value,
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
            time_series=lower_level_fields,
        )

        # Then
        time_series_dto.model_validate(time_series_dto)
        assert time_series_dto.metric_frequency == expected_metric_frequency_value

    @pytest.mark.parametrize(
        "metric_frequency_value",
        [
            (
                "d",
                "m",
                "day",
                "week",
                "month",
                "year",
                "D",
                "M",
                "W",
                "Q",
            )
        ],
    )
    def test_valid_payload_with_incorrect_metric_frequency_throws_error(
        self,
        metric_frequency_value: str,
        example_time_series_data: INCOMING_DATA_TYPE,
    ):
        """
        Given a payload containing an invalid metric frequency
        When the `TimeSeriesDTO` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_time_series_data

        # When
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        with pytest.raises(ValidationError):
            TimeSeriesDTO(
                metric_frequency=metric_frequency_value,
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
                time_series=lower_level_fields,
            )

    def test_in_reporting_delay_period_with_no_true_values_is_deemed_valid(
        self, example_time_series_data
    ):
        """
        Given a payload containing only False values
            for the `in_reporting_delay_period` fields
        When the `TimeSeriesDTO` model is initialized
        Then the model is deemed valid
        """
        # Given
        source_data = example_time_series_data
        time_series_data = source_data["time_series"]
        for data in time_series_data:
            data["in_reporting_delay_period"] = False

        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in time_series_data
        ]

        # When
        time_series_dto = TimeSeriesDTO(
            metric_frequency=source_data["metric_frequency"],
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
            time_series=lower_level_fields,
        )

        # Then
        time_series_dto.model_validate(time_series_dto)

    def test_in_reporting_delay_period_with_trailing_section_is_deemed_valid(
        self, example_time_series_data
    ):
        """
        Given a payload containing False values
            along with trailing True values
            for the `in_reporting_delay_period` fields
        When the `TimeSeriesDTO` model is initialized
        Then the model is deemed valid
        """
        # Given
        source_data = example_time_series_data
        time_series_data = source_data["time_series"]
        time_series_data[-1]["in_reporting_delay_period"] = True
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in time_series_data
        ]

        # When
        time_series_dto = TimeSeriesDTO(
            metric_frequency=source_data["metric_frequency"],
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
            time_series=lower_level_fields,
        )

        # Then
        time_series_dto.model_validate(time_series_dto)

    def test_in_reporting_delay_period_with_leading_section_is_deemed_invalid(
        self, example_time_series_data
    ):
        """
        Given a payload containing False values
            along with leading True values
            for the `in_reporting_delay_period` fields
        When the `TimeSeriesDTO` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_time_series_data
        time_series_data = source_data["time_series"]
        time_series_data[0]["in_reporting_delay_period"] = True
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in time_series_data
        ]

        # When / Then
        with pytest.raises(ValidationError):
            TimeSeriesDTO(
                metric_frequency=source_data["metric_frequency"],
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
                time_series=lower_level_fields,
            )
