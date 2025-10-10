import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from tests.unit.ingestion.data_transfer_models.base.test_validate_geography_type import (
    VALID_REGION_CODE,
)
from validation import enums
from validation.geography_code import UNITED_KINGDOM_GEOGRAPHY_CODE

VALID_ENGLAND_NATION_CODE = "E92000001"
VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE = "E06000059"
VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE = "E10000024"
VALID_NHS_REGION_CODE = "E40000003"
VALID_NHS_TRUST_CODE = "RY6"
VALID_UKHSA_REGION_CODE = "E45000017"
VALID_UKHSA_SUPER_REGION_CODE = "X25001"
VALID_GOVERNMENT_OFFICE_REGION_CODE = "E12000003"
VALID_INTEGRATED_CARE_BOARD_CODE = "QT6"
VALID_SUB_INTEGRATED_CARE_BOARD_CODE = "02G"


class TestIncomingBaseValidationForNHSTrustGeographyCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_NHS_TRUST_CODE,
            "RTE",
            "R0A",
            "NMJ45",
            "NRN01",
            "DN703",
            "NMJ0Y",
            "8CM63",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "NHS Trust"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NHS_TRUST.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_NHS_REGION_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for the "NHS Trust" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NHS_TRUST.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "geography_code",
        (
            "RV",
            "R",
            "RV56",
            "RV5678",
        ),
    )
    def test_geography_code_of_unsuitable_length_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a `geography_code` which is not 3 or 5 characters long
            for the "NHS Trust" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NHS_TRUST.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    def test_geography_code_must_not_start_with_special_character(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a `geography_code` which does not start with a letter or number
            for the "NHS Trust" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NHS_TRUST.value
        payload["geography_code"] = "!M3"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForLowerTierLocalAuthorityGeographyCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            "E06000024",
            "E07000090",
            "E07000127",
            "E08000025",
            "E08000005",
            "E09000025",
            "E09000009",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "Lower Tier Local Authority"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.LOWER_TIER_LOCAL_AUTHORITY.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_NHS_REGION_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "Lower Tier Local Authority" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.LOWER_TIER_LOCAL_AUTHORITY.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForUpperTierLocalAuthorityGeographyCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            "E06000024",
            "E07000090",
            "E07000127",
            "E08000025",
            "E08000005",
            "E09000025",
            "E09000009",
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "Upper Tier Local Authority"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UPPER_TIER_LOCAL_AUTHORITY.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_NHS_REGION_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "Upper Tier Local Authority" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UPPER_TIER_LOCAL_AUTHORITY.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForNHSRegionGeographyCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_NHS_REGION_CODE,
            "E40000005",
            "E40000010",
            "E40000007",
            "E40000008",
            "E40000006",
            "E40000009",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "NHS Region"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NHS_REGION.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "NHS Region" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NHS_REGION.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForNationGeographyCode:
    @pytest.mark.parametrize(
        "geography, geography_code",
        [
            ("England", "E92000001"),
            ("Scotland", "S92000003"),
            ("Wales", "W92000004"),
            ("Northern Ireland", "N92000002"),
        ],
    )
    def test_valid_geography_code_validates_successfully(
        self,
        geography: str,
        geography_code: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing a valid `geography_code` and `geography`
            for a `geography_type` of "Nation"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NATION.value
        payload["geography"] = geography
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography, geography_code",
        [
            ("England", "S92000003"),  # Incorrect geography code
            ("scotland", "S92000003"),  # Case sensitivity
            ("Welsh", "W92000004"),  # Incorrectly referenced country
            ("Ireland", "N92000002"),  # Incorrect geography code
            ("Fake Country", "E92000001"),  # Invalid country
        ],
    )
    def test_invalid_geography_invalidates_as_expected(
        self,
        geography: str,
        geography_code: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing an invalid `geography_code` or `geography`
            for a `geography_type` of "Nation"
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NATION.value
        payload["geography"] = geography
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_NHS_REGION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "Nation" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.NATION.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForUnitedKingdomGeographyCode:
    def test_valid_geography_code_validates_successfully(
        self,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing
            the only valid `geography_code` and `geography`
            for a `geography_type` of "United Kingdom"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UNITED_KINGDOM.value
        payload["geography"] = "United Kingdom"
        payload["geography_code"] = UNITED_KINGDOM_GEOGRAPHY_CODE

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_NHS_REGION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "United Kingdom" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UNITED_KINGDOM.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "geography",
        (
            "united kingdom",
            "UK",
            "England",
            "Great Britain",
        ),
    )
    def test_invalid_geography_name_throws_error(
        self, geography: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography`
            which is not valid for
            the "United Kingdom" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UNITED_KINGDOM.value
        payload["geography_code"] = UNITED_KINGDOM_GEOGRAPHY_CODE

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForGovernmentOfficeRegionGeographyCode:
    def test_valid_geography_code_validates_successfully(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "Government Office Region"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.GOVERNMENT_OFFICE_REGION.value
        payload["geography_code"] = VALID_GOVERNMENT_OFFICE_REGION_CODE

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_NHS_REGION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_ENGLAND_NATION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "Government Office Region" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.GOVERNMENT_OFFICE_REGION.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForRegionGeographyCode:
    def test_valid_geography_code_validates_successfully(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "Region"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.REGION.value
        payload["geography_code"] = VALID_REGION_CODE

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_NHS_REGION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_ENGLAND_NATION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for the "Region" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.REGION.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForUKHSARegionGeographyCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_UKHSA_REGION_CODE,
            "E45000009",
            "E45000019",
            "E45000016",
            "E45000001",
            "E45000018",
            "E45000020",
            "E45000010",
            "E45000005",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "UKHSA Region"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UKHSA_REGION.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_NHS_REGION_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "UKHSA Region" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UKHSA_REGION.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForUKHSASuperRegionGeographyCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_UKHSA_SUPER_REGION_CODE,
            "X25002",
            "X25003",
            "X25004",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "UKHSA Super-Region"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UKHSA_SUPER_REGION.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_NHS_TRUST_CODE,
            VALID_NHS_REGION_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
            "X2500A",
            "X2500@",
            "X25oo1",
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for
            the "UKHSA Super-Region" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.UKHSA_SUPER_REGION.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForIntegratedCareBoardCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_INTEGRATED_CARE_BOARD_CODE,
            "RTE",
            "R0A",
            "AD2",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "Integrated Care Board"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_NHS_REGION_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
            "1AB",
            "42N",
            "L2£",
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for the "Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "geography_code",
        (
            "R7",
            "R",
            "RV56",
            "RV5678",
        ),
    )
    def test_geography_code_of_unsuitable_length_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a `geography_code` which is not 3 or 5 characters long
            for the "Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    def test_geography_code_must_not_start_with_number(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a `geography_code` which does not start with a letter or number
            for the "Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = "3M2"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)


class TestIncomingBaseValidationForSubIntegratedCareBoardCode:
    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_SUB_INTEGRATED_CARE_BOARD_CODE,
            "3TE",
            "78A",
            "1D2",
            "H189A",
            "AD1B9",
            "AH1BD",
        ),
    )
    def test_valid_geography_code_validates_successfully(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a valid `geography_code` value
            for a `geography_type` of "Sub-Integrated Care Board"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.SUB_INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = geography_code

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "geography_code",
        (
            VALID_ENGLAND_NATION_CODE,
            VALID_LOWER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_NHS_REGION_CODE,
            VALID_UPPER_TIER_LOCAL_AUTHORITY_CODE,
            VALID_UKHSA_REGION_CODE,
            VALID_GOVERNMENT_OFFICE_REGION_CODE,
            "SAB",
            "A2N",
            "32%",
            "72A3N",
            "921DN",
            "U21D$",
        ),
    )
    def test_invalid_geography_code_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing a `geography_code`
            which is not valid for the "Sub-Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.SUB_INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "geography_code",
        (
            "R7",
            "R",
            "RV56",
            "RV5678",
        ),
    )
    def test_geography_code_of_unsuitable_length_throws_error(
        self, geography_code: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a `geography_code` which is not 3 or 5 characters long
            for the "Sub-Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.SUB_INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = geography_code

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    def test_three_length_geography_code_must_not_start_with_letter(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a 3-character length `geography_code`
            which starts with a letter
            for the "Sub-Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.SUB_INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = "AM2"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    def test_five_length_geography_code_must_not_start_with_number(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a 5-character length `geography_code`
            which starts with a number
            for the "Sub-Integrated Care Board" `geography_type`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["geography_type"] = enums.GeographyType.SUB_INTEGRATED_CARE_BOARD.value
        payload["geography_code"] = "2ASA6"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
