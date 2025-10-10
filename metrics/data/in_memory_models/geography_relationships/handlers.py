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
from validation.enums import GeographyType
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
