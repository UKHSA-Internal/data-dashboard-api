import pytest

from metrics.data.models.constants import (
    CHAR_COLUMN_MAX_CONSTRAINT,
    GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT,
    METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT,
    SEX_MAX_CHAR_CONSTRAINT,
)
from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


class TestAPITimeSeries:
    @pytest.mark.parametrize(
        "field_name, field_value",
        (
            ["metric_frequency", 0],
            ["age", "all"],
            ["month", 3],
            ["refresh_date", "2023-07-11"],
            ["metric_group", "deaths"],
            ["theme", "infectious_disease"],
            ["sub_theme", "respiratory"],
            ["topic", "COVID-19"],
            ["geography_type", "Government Office Region"],
            ["geography_code", "E45000001"],
            ["geography", "North West"],
            ["metric", "COVID-19_deaths_ONSByDay"],
            ["stratum", "default"],
            ["sex", "all"],
            ["year", "202"],
            ["apiweek", 11],
            ["date", "2020-03-10"],
            ["metric_value", 0],
        ),
    )
    def test_correct_fields_can_be_given_to_model(
        self, field_name: str, field_value: int | str
    ):
        """
        Given I have a valid field for the APITimeseries model.
        When I initialise a new instance of the api time series model passing a field.
        Then the value will be assigned to the model.
        """
        # Given
        field = field_value

        # When
        api_timeseries_model = FakeAPITimeSeries()
        setattr(api_timeseries_model, field_name, field_value)

        # Then
        field_value_from_model = getattr(api_timeseries_model, field_name)
        assert field_value_from_model == field

    @pytest.mark.parametrize(
        "field_name, field_value, field_max_length",
        (
            ["metric_frequency", 0, METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT],
            ["age", "all", CHAR_COLUMN_MAX_CONSTRAINT],
            ["metric_group", "deaths", CHAR_COLUMN_MAX_CONSTRAINT],
            ["theme", "infectious_disease", CHAR_COLUMN_MAX_CONSTRAINT],
            ["sub_theme", "respiratory", CHAR_COLUMN_MAX_CONSTRAINT],
            ["topic", "COVID-19", CHAR_COLUMN_MAX_CONSTRAINT],
            ["geography_type", "Government Office Region", CHAR_COLUMN_MAX_CONSTRAINT],
            ["geography_code", "E45000001", GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT],
            ["geography", "North West", CHAR_COLUMN_MAX_CONSTRAINT],
            ["metric", "COVID-19_deaths_ONSByDay", CHAR_COLUMN_MAX_CONSTRAINT],
            ["stratum", "default", CHAR_COLUMN_MAX_CONSTRAINT],
            ["sex", "all", SEX_MAX_CHAR_CONSTRAINT],
            ["metric_value", 0, CHAR_COLUMN_MAX_CONSTRAINT],
        ),
    )
    def test_correct_max_length_constraints_returned_from_model(
        self, field_name, field_value, field_max_length
    ):
        """
        Given I have a valid field for the API Timeseries model and a max_length constraint
        When I initialise a new instance of the api time series model passing in the field.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        field = field_value
        max_length_constraint = field_max_length

        # When
        api_timeseries_model = FakeAPITimeSeries()
        setattr(api_timeseries_model, field_name, field)
        field_concreate_field = next(
            field
            for field in api_timeseries_model._meta.concrete_fields
            if field.attname == field_name
        )

        # Then
        assert field_concreate_field.max_length == max_length_constraint
