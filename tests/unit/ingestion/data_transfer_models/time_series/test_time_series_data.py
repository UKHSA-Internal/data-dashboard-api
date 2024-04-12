import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.time_series import (
    InboundTimeSeriesSpecificFields,
    TimeSeriesDTO,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE


class TestTimeSeriesDTOTimeSeriesDataField:
    def test_validates_successfully_for_daily_frequency_data(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given multiple data points which are 1 day apart
        And a `metric_frequency` of "daily"
        When a `TimeSeriesDTO` model is initialized
        Then the model is deemed valid
        """
        # Given
        source_data = example_time_series_data
        metric_frequency = "daily"
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        # When
        time_series_dto = TimeSeriesDTO(
            metric_frequency=metric_frequency,
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
        time_series_dto.model_validate(obj=time_series_dto, strict=True)

    def test_validates_successfully_for_weekly_frequency_data(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given multiple data points which are 1 day apart
        And a `metric_frequency` of "weekly"
        When a `TimeSeriesDTO` model is initialized
        Then the model is deemed valid
        """
        # Given
        source_data = example_time_series_data
        metric_frequency = "weekly"
        source_data["time_series"][0]["date"] = "2022-11-01"
        source_data["time_series"][1]["date"] = "2022-11-08"
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        # When
        time_series_dto = TimeSeriesDTO(
            metric_frequency=metric_frequency,
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
        time_series_dto.model_validate(obj=time_series_dto, strict=True)

    def test_daily_frequency_data_with_contradicting_metric_frequency_is_deemed_invalid(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given data points which are actually 1 day apart
        And a `metric_frequency` of "weekly"
        When the `TimeSeriesDTO` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_time_series_data
        # Note the difference here, the records are still going to be 1 day apart
        # But the `metric_frequency` is "weekly"
        metric_frequency = "weekly"
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        # When / Then
        with pytest.raises(ValidationError):
            TimeSeriesDTO(
                metric_frequency=metric_frequency,
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

    def test_weekly_frequency_data_with_contradicting_metric_frequency_is_deemed_invalid(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given data points which are actually 7 days apart
        And a `metric_frequency` of "daily"
        When the `TimeSeriesDTO` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        source_data = example_time_series_data
        metric_frequency = "daily"
        # Note the difference here, the records are still going to be 7 days apart
        # But the `metric_frequency` is "daily"
        source_data["time_series"][0]["date"] = "2022-11-01"
        source_data["time_series"][1]["date"] = "2022-11-08"
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        # When / Then
        with pytest.raises(ValidationError):
            TimeSeriesDTO(
                metric_frequency=metric_frequency,
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
