import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.time_series import (
    InboundTimeSeriesSpecificFields,
    TimeSeriesDTO,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from metrics.data.enums import TimePeriod


class TestTimeSeriesDTOMetricFrequencyField:
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
