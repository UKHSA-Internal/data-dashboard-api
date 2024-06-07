from ingestion.utils import enums

NATION_GEOGRAPHY_CODE_PREFIX = "E92"
LOWER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIXES = ("E06", "E07", "E08", "E09")
UPPER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIXES = ("E06", "E07", "E08", "E09", "E10")
NHS_REGION_GEOGRAPHY_CODE_PREFIX = "E40"
UKHSA_REGION_GEOGRAPHY_CODE_PREFIX = "E45"
GOVERNMENT_OFFICE_REGION_GEOGRAPHY_CODE_PREFIX = "E12"


def validate_geography_code(*, geography_code: str, geography_type: str) -> str | None:
    """Validates the `geography_code` value to check it conforms to the accepted format

    Args:
        geography_code: The associated geography code being validated
        geography_type: The `geography_type` which was
            included in the payload alongside the `geography_code`

    Returns:
        The input `geography_code` unchanged if
        it has passed the validation checks.

    Raises:
         `ValueError`: If any of the validation checks fail

    """
    match geography_type:
        case enums.GeographyType.NATION.value:
            return _validate_nation_geography_code(geography_code=geography_code)
        case enums.GeographyType.UPPER_TIER_LOCAL_AUTHORITY.value:
            return _validate_upper_tier_local_authority_geography_code(
                geography_code=geography_code
            )
        case enums.GeographyType.LOWER_TIER_LOCAL_AUTHORITY.value:
            return _validate_lower_tier_local_authority_geography_code(
                geography_code=geography_code
            )
        case enums.GeographyType.UKHSA_REGION.value:
            return _validate_ukhsa_region_geography_code(geography_code=geography_code)
        case enums.GeographyType.NHS_REGION.value:
            return _validate_nhs_region_geography_code(geography_code=geography_code)
        case enums.GeographyType.GOVERNMENT_OFFICE_REGION.value:
            return _validate_government_office_region_geography_code(
                geography_code=geography_code
            )
        case enums.GeographyType.NHS_TRUST.value:
            return _validate_nhs_trust_geography_code(geography_code=geography_code)


def _validate_nation_geography_code(*, geography_code: str) -> str:
    if geography_code.startswith(NATION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_lower_tier_local_authority_geography_code(*, geography_code: str) -> str:
    if any(
        geography_code.startswith(prefix)
        for prefix in LOWER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIXES
    ):
        return geography_code

    raise ValueError


def _validate_upper_tier_local_authority_geography_code(*, geography_code: str) -> str:
    if any(
        geography_code.startswith(prefix)
        for prefix in UPPER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIXES
    ):
        return geography_code

    raise ValueError


def _validate_ukhsa_region_geography_code(*, geography_code: str) -> str:
    if geography_code.startswith(UKHSA_REGION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_nhs_region_geography_code(*, geography_code: str) -> str:
    if geography_code.startswith(NHS_REGION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_government_office_region_geography_code(*, geography_code: str) -> str:
    if geography_code.startswith(GOVERNMENT_OFFICE_REGION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_nhs_trust_geography_code(*, geography_code: str) -> str:
    allowable_nhs_trust_code_lengths = (3, 5)
    if len(geography_code) not in allowable_nhs_trust_code_lengths:
        raise ValueError

    if not geography_code[0].isalpha():
        raise ValueError

    return geography_code
