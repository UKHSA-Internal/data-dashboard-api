from metrics.data.in_memory_models.geography_relationships.nation_geography_codes import (
    NATION_LOOKUP,
)
from metrics.data.in_memory_models.geography_relationships.region_geography_codes import (
    REGION_LOOKUP,
)
from metrics.data.in_memory_models.geography_relationships.region_to_nation import (
    REGION_TO_NATION_LOOKUP,
)
from metrics.data.in_memory_models.geography_relationships.utla_to_region import (
    UTLA_TO_REGION_LOOKUP,
)
from validation.enums import (
    GeographyType,
    UKHSARegionUTLAs,
    GovOfficeRegionUTLAs,
    UTLAtoLTLA,
)
from validation.enums.gov_office_region_enums import GovOfficeRegion
from validation.enums.ukhsa_region_enums import UKHSARegion
from validation.enums.utla_ltla_enums import LTLAs, UTLAs
from validation.geography_code import UNITED_KINGDOM_GEOGRAPHY_CODE


class RelationshipsForGeographyTypeNotSupportedError(Exception): ...


GEOGRAPHY_RELATIONSHIP_TYPE = dict[str, str | None]
OPTIONAL_UPSTREAM_RELATIONSHIPS = list[GEOGRAPHY_RELATIONSHIP_TYPE] | None


def _get_united_kingdom_relationship():
    return {
        "geography_type": GeographyType.UNITED_KINGDOM.value,
        "name": GeographyType.UNITED_KINGDOM.value,
        "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
    }


def _get_relevant_nation_relationship(
    *, geography_code: str
) -> GEOGRAPHY_RELATIONSHIP_TYPE:
    try:
        nation_geography_name = REGION_TO_NATION_LOOKUP[geography_code]
        nation_geography_code = NATION_LOOKUP[nation_geography_name]
    except KeyError:
        nation_geography_name = None
        nation_geography_code = None

    return {
        "geography_type": GeographyType.NATION.value,
        "name": nation_geography_name,
        "geography_code": nation_geography_code,
    }


def _get_relevant_region_relationship(
    *, geography_code: str
) -> GEOGRAPHY_RELATIONSHIP_TYPE:
    try:
        region_geography_name = UTLA_TO_REGION_LOOKUP[geography_code]
        region_geography_code = REGION_LOOKUP[region_geography_name]
    except KeyError:
        region_geography_name = None
        region_geography_code = None

    return {
        "geography_type": "Region",
        "name": region_geography_name,
        "geography_code": region_geography_code,
    }


def _get_upstream_relationships_for_region(
    *, geography_code: str
) -> list[GEOGRAPHY_RELATIONSHIP_TYPE]:
    return [
        _get_united_kingdom_relationship(),
        _get_relevant_nation_relationship(geography_code=geography_code),
    ]


def _get_upstream_relationships_for_utla(
    *, geography_code: str
) -> list[GEOGRAPHY_RELATIONSHIP_TYPE]:
    relevant_region: dict[str, str] = _get_relevant_region_relationship(
        geography_code=geography_code
    )
    relevant_nation: dict[str, str] = _get_relevant_nation_relationship(
        geography_code=relevant_region["geography_code"]
    )
    return [_get_united_kingdom_relationship(), relevant_region, relevant_nation]


def get_upstream_relationships_for_geography(
    *, geography_code: str, geography_type: str
) -> OPTIONAL_UPSTREAM_RELATIONSHIPS:
    """Gets the upstream/parent geographies which are related to the given geography

    Notes:
        For a given geography this will get the geographies
        in which this given geography sits within.
        For example, the geography code associated with `Hackney`
        will sit within the `Region` of `London`, which sits
        within the `Nation` of `England and consequently
        the `United Kingdom`.
        As such the upstream relationships for `Hackney` would be:
        - Region = `London`
        - Nation = `England`
        - United Kingdom = United `Kingdom`

    If the geography type is not supported, then `None` will be returned

    Returns:
        A list of dicts, where each dict represents a relationship.
        Or None if the geography type is not supported.

    """

    if geography_type == GeographyType.NATION.value:
        return [_get_united_kingdom_relationship()]

    if geography_type == "Region":
        return _get_upstream_relationships_for_region(geography_code=geography_code)

    if geography_type == GeographyType.UPPER_TIER_LOCAL_AUTHORITY.value:
        return _get_upstream_relationships_for_utla(geography_code=geography_code)

    return None


def _get_ltla_from_utlas(utlas: list):
    ltlas = []
    for ltla in utlas:
        ltlas.extend(UTLAtoLTLA[ltla.upper()].return_list())

    return ltlas


def get_downstream_relationships_for_geography(
    geography_type: str, geography_name: str
):
    """Gets the downstream/child geographies which are related to the given geography

    Notes:
        For a given geography this will get the geographies
        which sit within this given geography.
        For example, given either the name or geography code associated
        with the `UKHSA Region` of `London`, all London UTLAs and LTLAs
        will be returned.

    If the geography type is not supported, then `None` will be returned

    Returns:
        An object containing lists of all downstream geographies
        Or None if the geography type is not supported.

    """

    if geography_type not in set(t.value for t in GeographyType):
        return None

    ukhsa_regions = []
    government_office_regions = []
    nhs_regions = []
    nhs_trusts = []
    upper_tier_local_authorities = []
    lower_tier_local_authorities = []

    key = geography_name.replace(" ", "_").upper()

    try:
        match geography_type:
            case "UKHSA Region":
                ukhsa_regions.append(UKHSARegion[key].value)
                utlas = UKHSARegionUTLAs[key].return_list()
                utla_names = UKHSARegionUTLAs[key].return_name_list()
                upper_tier_local_authorities.extend(utlas)
                lower_tier_local_authorities.extend(_get_ltla_from_utlas(utla_names))
            case "Government Office Region":
                government_office_regions.append(GovOfficeRegion[key].value)
                utlas = GovOfficeRegionUTLAs[key].return_list()
                utla_names = GovOfficeRegionUTLAs[key].return_name_list()
                upper_tier_local_authorities.extend(utlas)
                lower_tier_local_authorities.extend(_get_ltla_from_utlas(utla_names))
            case "Upper Tier Local Authority":
                upper_tier_local_authorities.extend(UTLAs[key].value)
                lower_tier_local_authorities.extend(_get_ltla_from_utlas([key]))
            case "Lower Tier Local Authority":
                lower_tier_local_authorities.extend(LTLAs[key].value)
    except KeyError as e:
        print(f"KEY ERROR: {e}")
        return None

    downstream_geographies = {
        "ukhsa_regions": ukhsa_regions,
        "government_office_regions": government_office_regions,
        "nhs_regions": nhs_regions,
        "nhs_trusts": nhs_trusts,
        "upper_tier_local_authorities": upper_tier_local_authorities,
        "lower_tier_local_authorities": lower_tier_local_authorities,
    }

    return downstream_geographies
