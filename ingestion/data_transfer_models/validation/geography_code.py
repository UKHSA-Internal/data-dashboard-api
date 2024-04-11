from ingestion.utils import enums

NATION_GEOGRAPHY_CODE_PREFIX = "E92"
LOWER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIXES = ("E06", "E07", "E08", "E09")
NHS_REGION_GEOGRAPHY_CODE_PREFIX = "E40"
UPPER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIX = "E10"
UKHSA_REGION_GEOGRAPHY_CODE_PREFIX = "E45"
GOVERNMENT_OFFICE_REGION_GEOGRAPHY_CODE_PREFIX = "E12"


def validate_geography_code(geography_code: str, geography_type: str) -> str | None:
    match geography_type:
        case enums.GeographyType.NATION.value:
            return _validate_nation_geography_code(geography_code=geography_code)
        case enums.GeographyType.UPPER_TIER_LOCAL_AUTHORITY.value:
            return _validate_upper_tier_local_authority_geography_code(
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
        case enums.GeographyType.LOWER_TIER_LOCAL_AUTHORITY.value:
            return _validate_lower_tier_local_authority_geography_code(
                geography_code=geography_code
            )
        case enums.GeographyType.NHS_TRUST.value:
            return _validate_nhs_trust_geography_code(geography_code=geography_code)


def _validate_nation_geography_code(geography_code: str) -> str:
    if geography_code.startswith(NATION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_upper_tier_local_authority_geography_code(geography_code: str) -> str:
    if geography_code.startswith(UPPER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_lower_tier_local_authority_geography_code(geography_code: str) -> str:
    if any(
        geography_code.startswith(prefix)
        for prefix in LOWER_TIER_LOCAL_AUTHORITY_GEOGRAPHY_CODE_PREFIXES
    ):
        return geography_code

    raise ValueError


def _validate_ukhsa_region_geography_code(geography_code: str) -> str:
    if geography_code.startswith(UKHSA_REGION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_nhs_region_geography_code(geography_code: str) -> str:
    if geography_code.startswith(NHS_REGION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_government_office_region_geography_code(geography_code: str) -> str:
    if geography_code.startswith(GOVERNMENT_OFFICE_REGION_GEOGRAPHY_CODE_PREFIX):
        return geography_code
    raise ValueError


def _validate_nhs_trust_geography_code(geography_code: str) -> str:
    if len(geography_code) not in (3, 5):
        raise ValueError

    if not geography_code[0].isalpha():
        raise ValueError

    return geography_code
