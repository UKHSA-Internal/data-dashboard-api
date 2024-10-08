import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.metrics_interface.interface import DataSourceFileType

VALID_PARENT_THEME = "infectious_disease"
VALID_CHILD_THEME = "respiratory"
VALID_TOPIC = "Rhinovirus"
VALID_METRIC = "rhinovirus_testing_positivityByWeek"
VALID_METRIC_GROUP = DataSourceFileType.testing.value
VALID_GEOGRAPHY_TYPE = "Nation"
VALID_GEOGRAPHY = "England"
VALID_GEOGRAPHY_CODE = "E92000001"
VALID_AGE = "all"
VALID_SEX = "all"
VALID_STRATUM = "default"
VALID_REFRESH_DATE_IN_DATE_FORMAT = "2023-11-20"
VALID_REFRESH_DATE_IN_DATETIME_FORMAT = "2024-01-01 14:20:03"


class TestIncomingBaseValidation:
    def test_valid_payload_is_deemed_valid(self):
        """
        Given a payload containing valid values
        When the `IncomingHeadlineValidation` model is initialized
        Then model is deemed valid
        """
        # Given / When
        incoming_base_validation = IncomingBaseDataModel(
            parent_theme=VALID_PARENT_THEME,
            child_theme=VALID_CHILD_THEME,
            topic=VALID_TOPIC,
            metric_group=VALID_METRIC_GROUP,
            metric=VALID_METRIC,
            geography_type=VALID_GEOGRAPHY_TYPE,
            geography=VALID_GEOGRAPHY,
            geography_code=VALID_GEOGRAPHY_CODE,
            age=VALID_AGE,
            sex=VALID_SEX,
            stratum=VALID_STRATUM,
            refresh_date=VALID_REFRESH_DATE_IN_DATE_FORMAT,
        )

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "input_sex_value, expected_output_sex_value",
        [
            ("Male", "m"),
            ("Female", "f"),
            ("All", "all"),
        ],
    )
    def test_sex_value_of_valid_payload_is_cast_to_correct_output(
        self, input_sex_value: str, expected_output_sex_value: str
    ):
        """
        Given a payload containing valid values
        When the `IncomingHeadlineValidation` model is initialized
        Then model is deemed valid
        And the correct value is cast for the output sex field
        """
        # Given
        payload_sex_value = input_sex_value

        # When
        incoming_base_validation = IncomingBaseDataModel(
            parent_theme=VALID_PARENT_THEME,
            child_theme=VALID_CHILD_THEME,
            topic=VALID_TOPIC,
            metric_group=VALID_METRIC_GROUP,
            metric=VALID_METRIC,
            geography_type=VALID_GEOGRAPHY_TYPE,
            geography=VALID_GEOGRAPHY,
            geography_code=VALID_GEOGRAPHY_CODE,
            age=VALID_AGE,
            sex=payload_sex_value,
            stratum=VALID_STRATUM,
            refresh_date=VALID_REFRESH_DATE_IN_DATE_FORMAT,
        )

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )
        assert incoming_base_validation.sex == expected_output_sex_value

    def test_refresh_date_as_date_defaults_to_midnight(self):
        """
        Given a payload containing valid values
        And a `refresh_date` provided as a date
        When the `IncomingHeadlineValidation` model is initialized
        Then model is deemed valid
        And the `refresh_date` is set to midnight of that date
        """
        # Given
        refresh_date = VALID_REFRESH_DATE_IN_DATE_FORMAT

        # When
        incoming_base_validation = IncomingBaseDataModel(
            parent_theme=VALID_PARENT_THEME,
            child_theme=VALID_CHILD_THEME,
            topic=VALID_TOPIC,
            metric_group=VALID_METRIC_GROUP,
            metric=VALID_METRIC,
            geography_type=VALID_GEOGRAPHY_TYPE,
            geography=VALID_GEOGRAPHY,
            geography_code=VALID_GEOGRAPHY_CODE,
            age=VALID_AGE,
            sex=VALID_SEX,
            stratum=VALID_STRATUM,
            refresh_date=refresh_date,
        )

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

        assert (
            str(incoming_base_validation.refresh_date)
            == f"{refresh_date} 00:00:00+00:00"
        )

    def test_refresh_date_as_timestamp_is_validated(self):
        """
        Given a payload containing valid values
        And a `refresh_date` provided as a timestamp
        When the `IncomingHeadlineValidation` model is initialized
        Then model is deemed valid
        And the `refresh_date` is set to the correct timestamp
        """
        # Given
        refresh_date = VALID_REFRESH_DATE_IN_DATETIME_FORMAT

        # When
        incoming_base_validation = IncomingBaseDataModel(
            parent_theme=VALID_PARENT_THEME,
            child_theme=VALID_CHILD_THEME,
            topic=VALID_TOPIC,
            metric_group=VALID_METRIC_GROUP,
            metric=VALID_METRIC,
            geography_type=VALID_GEOGRAPHY_TYPE,
            geography=VALID_GEOGRAPHY,
            geography_code=VALID_GEOGRAPHY_CODE,
            age=VALID_AGE,
            sex=VALID_SEX,
            stratum=VALID_STRATUM,
            refresh_date=refresh_date,
        )

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

        assert str(incoming_base_validation.refresh_date) == f"{refresh_date}+00:00"

    def test_raises_error_when_parent_theme_not_recognized(self):
        """
        Given an otherwise valid payload containing
            an invalid `parent_theme` value
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_parent_theme = "non-existent-parent-theme"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(
                parent_theme=fake_parent_theme,
                child_theme=VALID_CHILD_THEME,
                topic=VALID_TOPIC,
                metric_group=VALID_METRIC_GROUP,
                metric=VALID_METRIC,
                geography_type=VALID_GEOGRAPHY_TYPE,
                geography=VALID_GEOGRAPHY,
                geography_code=VALID_GEOGRAPHY_CODE,
                age=VALID_AGE,
                sex=VALID_SEX,
                stratum=VALID_STRATUM,
                refresh_date=VALID_REFRESH_DATE_IN_DATE_FORMAT,
            )

    def test_raises_error_when_metric_group_not_recognized(self):
        """
        Given an otherwise valid payload
            containing an invalid metric group value
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_metric_group = "non-existent-metric-group"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(
                parent_theme=VALID_PARENT_THEME,
                child_theme=VALID_CHILD_THEME,
                topic=VALID_TOPIC,
                metric_group=fake_metric_group,
                metric=VALID_METRIC,
                geography_type=VALID_GEOGRAPHY_TYPE,
                geography=VALID_GEOGRAPHY,
                geography_code=VALID_GEOGRAPHY_CODE,
                age=VALID_AGE,
                sex=VALID_SEX,
                stratum=VALID_STRATUM,
                refresh_date=VALID_REFRESH_DATE_IN_DATE_FORMAT,
            )

    @pytest.mark.parametrize(
        "invalid_geography_code", ["xy", "this-geography-code-is-too-long"]
    )
    def test_raises_error_when_invalid_geography_code_provided(
        self, invalid_geography_code: str
    ):
        """
        Given an otherwise valid payload
            containing an invalid geography code value
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_geography_code = invalid_geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(
                parent_theme=VALID_PARENT_THEME,
                child_theme=VALID_CHILD_THEME,
                topic=VALID_TOPIC,
                metric_group=VALID_METRIC_GROUP,
                metric=VALID_METRIC,
                geography_type=VALID_GEOGRAPHY_TYPE,
                geography=VALID_GEOGRAPHY,
                geography_code=fake_geography_code,
                age=VALID_AGE,
                sex=VALID_SEX,
                stratum=VALID_STRATUM,
                refresh_date=VALID_REFRESH_DATE_IN_DATE_FORMAT,
            )

    def test_raises_error_for_deprecated_geography(self):
        """
        Given an otherwise valid payload
            containing a deprecated geography
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        deprecated_geography_name = (
            "St Helens and Knowsley Teaching Hospitals NHS Trust"
        )
        geography_type = "NHS Trust"
        geography_code = "E40000001"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(
                parent_theme=VALID_PARENT_THEME,
                child_theme=VALID_CHILD_THEME,
                topic=VALID_TOPIC,
                metric_group=VALID_METRIC_GROUP,
                metric=VALID_METRIC,
                geography_type=geography_type,
                geography=deprecated_geography_name,
                geography_code=geography_code,
                age=VALID_AGE,
                sex=VALID_SEX,
                stratum=VALID_STRATUM,
                refresh_date=VALID_REFRESH_DATE_IN_DATE_FORMAT,
            )
