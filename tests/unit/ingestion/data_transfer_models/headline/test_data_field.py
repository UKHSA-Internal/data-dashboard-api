import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.headline import (
    HeadlineDTO,
    InboundHeadlineSpecificFields,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE


class TestHeadlineDTOForDataField:
    def test_multiple_data_points_are_deemed_invalid(
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
        multiple_data_points = [
            InboundHeadlineSpecificFields(**individual_source_data)
            for individual_source_data in source_data["data"]
        ] * 3

        # When
        with pytest.raises(ValidationError):
            HeadlineDTO(
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
                data=multiple_data_points,
            )
