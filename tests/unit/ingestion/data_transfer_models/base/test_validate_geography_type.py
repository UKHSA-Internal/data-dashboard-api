import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.data_transfer_models.validation.geography_code import (
    UNITED_KINGDOM_GEOGRAPHY_CODE,
)

VALID_ENGLAND_NATION_CODE = "E92000001"
VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE = "E06000059"
VALID_NHS_REGION_CODE = "E40000003"
VALID_NHS_TRUST_CODE = "RY6"
VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE = "E10000024"
VALID_UKHSA_REGION_CODE = "E45000017"
VALID_GOVERNMENT_OFFICE_REGION_CODE = "E12000003"


class TestIncomingBaseValidationForGeographyType:
    @pytest.mark.parametrize(
        "geography_type, geography_code",
        (
            ("United Kingdom", UNITED_KINGDOM_GEOGRAPHY_CODE),
            ("Nation", VALID_ENGLAND_NATION_CODE),
            ("Lower Tier Local Authority", VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE),
            ("NHS Region", VALID_NHS_REGION_CODE),
            ("NHS Trust", VALID_NHS_TRUST_CODE),
            ("Upper Tier Local Authority", VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE),
            ("UKHSA Region", VALID_UKHSA_REGION_CODE),
            ("Government Office Region", VALID_GOVERNMENT_OFFICE_REGION_CODE),
        ),
    )
    def test_valid_geography_type_value_is_deemed_valid(
        self,
        geography_type: str,
        geography_code: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing a valid `geography_type` value
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = geography_type
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_type, geography_code",
        (
            ("united kingdom", UNITED_KINGDOM_GEOGRAPHY_CODE),
            ("uk", UNITED_KINGDOM_GEOGRAPHY_CODE),
            ("nation", VALID_ENGLAND_NATION_CODE),
            ("national", VALID_ENGLAND_NATION_CODE),
            ("NATION", VALID_ENGLAND_NATION_CODE),
            ("NATIONAL", VALID_ENGLAND_NATION_CODE),
            ("lower tier local authority", VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE),
            ("LTLA", VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE),
            ("ltla", VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE),
            ("NHS", VALID_NHS_REGION_CODE),
            ("NHS REGION", VALID_NHS_REGION_CODE),
            ("NHS Regions", VALID_NHS_REGION_CODE),
            ("NHS Trusts", VALID_NHS_TRUST_CODE),
            ("NHS trusts", VALID_NHS_TRUST_CODE),
            ("upper tier local authority", VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE),
            ("UTLA", VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE),
            ("utla", VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE),
            ("ukhsa region", VALID_UKHSA_REGION_CODE),
            ("UKHSA Regions", VALID_UKHSA_REGION_CODE),
            ("government office region", VALID_GOVERNMENT_OFFICE_REGION_CODE),
            ("Government Office Regions", VALID_GOVERNMENT_OFFICE_REGION_CODE),
        ),
    )
    def test_invalid_geography_type_value_throws_error(
        self,
        geography_type: str,
        geography_code: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing an invalid `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = geography_type
        payload["geography_code"] = geography_code

        # When
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
