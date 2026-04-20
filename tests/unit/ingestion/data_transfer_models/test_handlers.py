from unittest import mock

import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.handlers import (
    build_headline_dto_from_source,
    build_time_series_dto_from_source,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from validation.data_transfer_models.base import MissingFieldError
from validation.is_public import MISSING_IS_PUBLIC_FIELD_ERROR, NOT_METRIC_ERROR

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
COMMON_FIELDS = [
    "parent_theme",
    "child_theme",
    "topic",
    "metric_group",
    "metric",
    "geography_type",
    "geography",
    "geography_code",
    "age",
    "sex",
    "stratum",
    "refresh_date",
]
COMMON_FIELDS_EXCLUDING_METRIC = [field for field in COMMON_FIELDS if field != "metric"]
TIME_SERIES_SPECIFIC_FIELDS = [
    "epiweek",
    "date",
]

HEADLINE_SPECIFIC_FIELDS = [
    "period_start",
    "period_end",
]


class TestBuildTimeSeriesDTOFromSource:
    def test_extracts_common_fields_from_source_correctly(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming time series source data
        When `build_time_series_dto_from_source()` is called
        Then the returned `TimeSeriesDTO` is enriched with the correct fields
        """
        # Given
        source_data = example_time_series_data

        # When
        time_series_dto = build_time_series_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        # Check that the upper level/common fields are extracted properly
        assert time_series_dto.parent_theme == source_data["parent_theme"]
        assert time_series_dto.child_theme == source_data["child_theme"]
        assert time_series_dto.topic == source_data["topic"]
        assert time_series_dto.metric_group == source_data["metric_group"]
        assert time_series_dto.metric == source_data["metric"]
        assert time_series_dto.geography_type == source_data["geography_type"]
        assert time_series_dto.geography == source_data["geography"]
        assert time_series_dto.geography_code == source_data["geography_code"]
        assert time_series_dto.age == source_data["age"]
        assert time_series_dto.sex == source_data["sex"]
        assert time_series_dto.stratum == source_data["stratum"]
        assert (
            time_series_dto.refresh_date.strftime("%Y-%m-%d")
            == source_data["refresh_date"]
        )

    def test_extracts_lower_level_specific_fields_from_source_correctly(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming time series source data
        When `build_time_series_dto_from_source()` is called
        Then the returned `TimeSeriesDTO` is enriched
            with the correct lower level-specific fields
        """
        # Given
        source_data = example_time_series_data

        # When
        time_series_dto = build_time_series_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        # Check that the lower level/specific fields are extracted properly
        for specific_field_group in time_series_dto.time_series:
            rebuild_specific_fields = {
                "epiweek": specific_field_group.epiweek,
                "date": specific_field_group.date.strftime(DATE_FORMAT),
                "metric_value": specific_field_group.metric_value,
                "embargo": specific_field_group.embargo.strftime(DATETIME_FORMAT),
                "is_public": specific_field_group.is_public,
            }
            assert rebuild_specific_fields in source_data["time_series"]

    def test_raises_error_when_is_public_is_not_provided(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming time series source data
            which omits the `is_public` field
        When `build_time_series_dto_from_source()` is called
        Then a `ValueError` is raised
        """
        # Given
        source_data = example_time_series_data
        for time_series_data in source_data["time_series"]:
            time_series_data.pop("is_public")

        # When
        with pytest.raises(ValueError, match=MISSING_IS_PUBLIC_FIELD_ERROR):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @mock.patch("validation.is_public.ALLOW_MISSING_IS_PUBLIC_FIELD", new=True)
    @mock.patch(
        "ingestion.data_transfer_models.time_series.ALLOW_MISSING_IS_PUBLIC_FIELD",
        new=True,
    )
    def test_defaults_is_public_to_true_when_not_provided_and_override_on(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        # Given
        source_data = example_time_series_data
        for time_series_data in source_data["time_series"]:
            time_series_data.pop("is_public")

        # When
        time_series_dto = build_time_series_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        assert time_series_dto.time_series[0].is_public is True
        assert time_series_dto.time_series[1].is_public is True

    def test_filters_out_individual_data_points_with_metric_value_of_none(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming time series source data
            of which 1 of the time series contains None for the `metric_value`
        When `build_time_series_dto_from_source()` is called
        Then the metric_value of None is filtered out
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"][0]["metric_value"] = None

        # When
        time_series_dto = build_time_series_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        metric_values = [x.metric_value for x in time_series_dto.time_series]
        assert None not in metric_values

    @pytest.mark.parametrize("field", COMMON_FIELDS_EXCLUDING_METRIC)
    def test_raises_error_when_none_value_provided_to_common_field(
        self,
        field: str,
        example_time_series_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given otherwise valid incoming source data
            which contains a field with a None value
        When `build_time_series_dto_from_source()` is called
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data[field] = None

        # When / Then
        with pytest.raises(ValidationError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_type_error_when_none_value_provided_to_metric_field(
        self,
        example_time_series_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        # Given
        source_data = example_time_series_data
        source_data["metric"] = None

        # When / Then
        with pytest.raises(TypeError, match=NOT_METRIC_ERROR):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @pytest.mark.parametrize("field", COMMON_FIELDS_EXCLUDING_METRIC)
    def test_raises_error_when_field_is_missing_from_source_data(
        self,
        field: str,
        example_time_series_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given otherwise valid incoming source data
            which contains a field with a None value
        When `build_time_series_dto_from_source()` is called
        Then a `ValueError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data.pop(field)

        # When / Then
        with pytest.raises(MissingFieldError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_type_error_when_metric_field_is_missing_from_source_data(
        self,
        example_time_series_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        # Given
        source_data = example_time_series_data
        source_data.pop("metric")

        # When / Then
        with pytest.raises(TypeError, match=NOT_METRIC_ERROR):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @pytest.mark.parametrize("field", TIME_SERIES_SPECIFIC_FIELDS)
    def test_raises_error_when_none_value_provided_to_lower_level_field(
        self,
        field: str,
        example_time_series_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given otherwise valid incoming source data
            which contains a lower level/specific field with a None value
        When `build_time_series_dto_from_source()` is called
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"][0][field] = None

        # When / Then
        with pytest.raises(ValidationError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_embargo_is_missing_from_source_data(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming source data
            which contains a field with a None value
        When `build_time_series_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"][0].pop("embargo")

        # When / Then
        with pytest.raises(MissingFieldError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @pytest.mark.parametrize("field", TIME_SERIES_SPECIFIC_FIELDS)
    def test_raises_error_when_lower_level_field_is_missing_from_source_data(
        self,
        field: str,
        example_time_series_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given otherwise valid incoming source data
            which contains a field with a None value
        When `build_time_series_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"][0].pop(field)

        # When / Then
        with pytest.raises(MissingFieldError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_metric_value_is_missing_from_source_data(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming source data
            which contains a `metric_value` of None
        When `build_time_series_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"][0].pop("metric_value")

        # When / Then
        with pytest.raises(MissingFieldError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_time_series_field_is_missing_from_source_data(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming source data
            which does not contain a "time_series" field
        When `build_time_series_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data.pop("time_series")

        # When / Then
        with pytest.raises(MissingFieldError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_time_series_field_is_none_in_source_data(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming source data
            which contains a None value for the "time_series" field
        When `build_time_series_dto_from_source()` is called
        Then a `ValueError` is raised
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"] = None

        # When / Then
        with pytest.raises(ValueError):
            build_time_series_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_builds_dto_when_time_series_is_empty(
        self, example_time_series_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given incoming time series source data with an empty "time_series" list
        When `build_time_series_dto_from_source()` is called
        Then a `TimeSeriesDTO` is returned with no time series entries
        """
        # Given
        source_data = example_time_series_data
        source_data["time_series"] = []

        # When
        time_series_dto = build_time_series_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        assert time_series_dto.time_series == []


class TestBuildHeadlineDTOFromSource:
    def test_extracts_common_fields_from_source_correctly(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming headline source data
        When `build_headline_dto_from_source()` is called
        Then the returned `HeadlineDTO` is enriched with the correct fields
        """
        # Given
        source_data = example_headline_data

        # When
        headline_dto = build_headline_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        # Check that the upper level/common fields are extracted properly
        assert headline_dto.parent_theme == source_data["parent_theme"]
        assert headline_dto.child_theme == source_data["child_theme"]
        assert headline_dto.topic == source_data["topic"]
        assert headline_dto.metric_group == source_data["metric_group"]
        assert headline_dto.metric == source_data["metric"]
        assert headline_dto.geography_type == source_data["geography_type"]
        assert headline_dto.geography == source_data["geography"]
        assert headline_dto.geography_code == source_data["geography_code"]
        assert headline_dto.age == source_data["age"]
        assert headline_dto.sex == source_data["sex"]
        assert headline_dto.stratum == source_data["stratum"]
        assert (
            headline_dto.refresh_date.strftime("%Y-%m-%d")
            == source_data["refresh_date"]
        )

    def test_extracts_lower_level_specific_fields_from_source_correctly(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming headline source data
        When `build_headline_dto_from_source()` is called
        Then the returned `HeadlineDTO` is enriched
            with the correct lower level-specific fields
        """
        # Given
        source_data = example_headline_data

        # When
        headline_dto = build_headline_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        # Check that the lower level/specific fields are extracted properly
        for specific_field_group in headline_dto.data:
            rebuild_specific_fields = {
                "period_start": specific_field_group.period_start.strftime(DATE_FORMAT),
                "period_end": specific_field_group.period_end.strftime(DATE_FORMAT),
                "upper_confidence": specific_field_group.upper_confidence,
                "metric_value": specific_field_group.metric_value,
                "lower_confidence": specific_field_group.lower_confidence,
                "embargo": specific_field_group.embargo.strftime(DATETIME_FORMAT),
                "is_public": specific_field_group.is_public,
            }
            assert rebuild_specific_fields in source_data["data"]

    def test_raises_error_when_is_public_is_not_provided(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming headline source data
            which omits the `is_public` field
        When `build_headline_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_headline_data
        for headline_data in source_data["data"]:
            headline_data.pop("is_public")

        # When
        with pytest.raises(ValueError, match=MISSING_IS_PUBLIC_FIELD_ERROR):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @mock.patch("validation.is_public.ALLOW_MISSING_IS_PUBLIC_FIELD", new=True)
    @mock.patch(
        "ingestion.data_transfer_models.headline.ALLOW_MISSING_IS_PUBLIC_FIELD",
        new=True,
    )
    def test_defaults_is_public_to_true_when_not_provided(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        # Given
        source_data = example_headline_data
        for headline_data in source_data["data"]:
            headline_data.pop("is_public")

        # When
        headline_dto = build_headline_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        assert headline_dto.data[0].is_public is True
        assert headline_dto.data[1].is_public is True

    def test_filters_out_individual_data_points_with_metric_value_of_none(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given valid incoming headline source data
            of which 1 of the headlines contains None for the `metric_value`
        When `build_headline_dto_from_source()` is called
        Then the metric_value of None is filtered out
        """
        # Given
        source_data = example_headline_data
        source_data["data"][0]["metric_value"] = None

        # When
        headline_dto = build_headline_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        metric_values = [x.metric_value for x in headline_dto.data]
        assert None not in metric_values

    @pytest.mark.parametrize("field", COMMON_FIELDS_EXCLUDING_METRIC)
    def test_raises_error_when_none_value_provided_to_common_field(
        self, field: str, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which contains a field with a None value
        When `build_headline_dto_from_source()` is called
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data[field] = None

        # When / Then
        with pytest.raises(ValidationError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_type_error_when_none_value_provided_to_metric_field(
        self,
        example_headline_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        # Given
        source_data = example_headline_data
        source_data["metric"] = None

        # When / Then
        with pytest.raises(TypeError, match=NOT_METRIC_ERROR):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @pytest.mark.parametrize("field", COMMON_FIELDS_EXCLUDING_METRIC)
    def test_raises_error_when_field_is_missing_from_source_data(
        self, field: str, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which contains a field with a None value
        When `build_headline_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data.pop(field)

        # When / Then
        with pytest.raises(MissingFieldError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_type_error_when_metric_field_is_missing_from_source_data(
        self,
        example_headline_data: INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        # Given
        source_data = example_headline_data
        source_data.pop("metric")

        # When / Then
        with pytest.raises(TypeError, match=NOT_METRIC_ERROR):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @pytest.mark.parametrize("field", HEADLINE_SPECIFIC_FIELDS)
    def test_raises_error_when_none_value_provided_to_lower_level_field(
        self, field: str, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which contains a lower level/specific field with a None value
        When `build_headline_dto_from_source()` is called
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data["data"][0][field] = None

        # When / Then
        with pytest.raises(ValidationError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    @pytest.mark.parametrize("field", HEADLINE_SPECIFIC_FIELDS)
    def test_raises_error_when_lower_level_field_is_missing_from_source_data(
        self, field: str, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which contains a field with a None value
        When `build_headline_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data["data"][0].pop(field)

        # When / Then
        with pytest.raises(MissingFieldError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_embargo_is_missing_from_source_data(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which contains a field with a None value
        When `build_headline_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data["data"][0].pop("embargo")

        # When / Then
        with pytest.raises(MissingFieldError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_metric_value_is_missing_from_source_data(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which contains a `metric_value` of None
        When `build_headline_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data["data"][0].pop("metric_value")

        # When / Then
        with pytest.raises(MissingFieldError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_time_series_field_is_missing_from_source_data(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming headline source data
            which does not contain a "data" field
        When `build_headline_dto_from_source()` is called
        Then a `MissingFieldError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data.pop("data")

        # When / Then
        with pytest.raises(MissingFieldError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_raises_error_when_time_series_field_is_none_in_source_data(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given otherwise valid incoming source data
            which contains a None value for the "time_series" field
        When `build_headline_dto_from_source()` is called
        Then a `ValueError` is raised
        """
        # Given
        source_data = example_headline_data
        source_data["data"] = None

        # When / Then
        with pytest.raises(ValueError):
            build_headline_dto_from_source(
                source_data=source_data, filename=test_filename
            )

    def test_builds_dto_when_data_is_empty(
        self, example_headline_data: INCOMING_DATA_TYPE, test_filename: str
    ):
        """
        Given incoming headline source data with an empty "data" list
        When `build_headline_dto_from_source()` is called
        Then a `HeadlineDTO` is returned with no data entries
        """
        # Given
        source_data = example_headline_data
        source_data["data"] = []

        # When
        headline_dto = build_headline_dto_from_source(
            source_data=source_data, filename=test_filename
        )

        # Then
        assert headline_dto.data == []
