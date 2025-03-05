import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.utils.enums import GeographyType
from tests.unit.ingestion.data_transfer_models.validation.unsuccessful.parameters import (
    INVALID_PARAMETERS,
)


@pytest.mark.parametrize("invalid_input_parameters", INVALID_PARAMETERS)
def test_raises_error_with_invalid_parameters(
    invalid_input_parameters: tuple[str, str, str, str],
):
    """
    Given an invalid set of parameters
    When the `IncomingBaseDataModel` is validated
    Then a `ValidationError` is raised
    """
    # Given / When / Then
    with pytest.raises(ValidationError):
        IncomingBaseDataModel(
            parent_theme=invalid_input_parameters[0],
            child_theme=invalid_input_parameters[1],
            topic=invalid_input_parameters[2],
            metric=invalid_input_parameters[3],
            metric_group=invalid_input_parameters[4],
            geography_type=GeographyType.NATION.value,
            geography="England",
            geography_code="E92000001",
            age="all",
            sex="all",
            stratum="default",
            refresh_date="2024-01-01 14:20:03",
        )
