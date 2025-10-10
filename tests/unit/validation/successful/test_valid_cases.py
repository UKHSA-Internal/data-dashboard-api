import pytest

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.utils.enums import GeographyType
from tests.unit.validation.successful.parameters import VALID_PARAMETERS


@pytest.mark.parametrize("valid_input_parameters", VALID_PARAMETERS)
def test_passes_validation_with_valid_parameters(
    valid_input_parameters: tuple[str, str, str, str],
):
    """
    Given a valid set of parameters
    When the `IncomingBaseDataModel` is validated
    Then no error is raised
    """
    # Given / When
    incoming_base_validation = IncomingBaseDataModel(
        parent_theme=valid_input_parameters[0],
        child_theme=valid_input_parameters[1],
        topic=valid_input_parameters[2],
        metric=valid_input_parameters[3],
        metric_group=valid_input_parameters[4],
        geography_type=GeographyType.NATION.value,
        geography="England",
        geography_code="E92000001",
        age="all",
        sex="all",
        stratum="default",
        refresh_date="2024-01-01 14:20:03",
    )

    # Then
    incoming_base_validation.model_validate(
        incoming_base_validation,
        strict=True,
    )
