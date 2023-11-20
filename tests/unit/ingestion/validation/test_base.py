import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.file_ingestion import DataSourceFileType
from ingestion.validation.base import IncomingBaseValidation

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
VALID_REFRESH_DATE = "2023-11-20"


class TestIncomingBaseValidation:
    def test_valid_payload_is_deemed_valid(self):
        """
        Given a payload containing valid values
        When the `IncomingHeadlineValidation` model is initialized
        Then model is deemed valid
        """
        # Given / When
        incoming_headline_validation = IncomingBaseValidation(
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
            refresh_date=VALID_REFRESH_DATE,
        )

        # Then
        incoming_headline_validation.model_validate(
            incoming_headline_validation,
            strict=True,
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
            IncomingBaseValidation(
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
                refresh_date=VALID_REFRESH_DATE,
            )

    @pytest.mark.parametrize(
        "invalid_geography_code", ["xy", "this-geography-code-is-too-long"]
    )
    def test_raises_error_when_invalid_geography_code_provided(
        self, invalid_geography_code: str
    ):
        """
        Given an otherwise valid payload
            containing an invalid geography coce value
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_geography_code = invalid_geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseValidation(
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
                refresh_date=VALID_REFRESH_DATE,
            )
