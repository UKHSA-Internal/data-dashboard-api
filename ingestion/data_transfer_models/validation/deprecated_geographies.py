def validate_deprecated_geographies(
    *, geography_name: str, geography_code: str, geography_type: str
) -> None:
    """Checks to see if the given geography information is not deprecated

    Args:
        `geography_name`: The name of the geography e.g. "England"
        `geography_code`: The code associated with the geography
            e.g. "E92000001"
        `geography_type`: The type associated with the geography
            e.g. "Nation"

    Returns:
        None

    Raises:
        `ValueError`: If the given geography information
            is deemed to match any of the deprecated geographies

    """
    _validate_st_helens_trust(
        geography_name=geography_name, geography_type=geography_type
    )
    _validate_midlands_code(
        geography_name=geography_name,
        geography_code=geography_code,
        geography_type=geography_type,
    )
    _validate_northeast_code(
        geography_name=geography_name,
        geography_code=geography_code,
        geography_type=geography_type,
    )


def _validate_st_helens_trust(*, geography_name: str, geography_type: str) -> None:
    if (
        geography_name == "St Helens and Knowsley Teaching Hospitals NHS Trust"
        and geography_type == "NHS Trust"
    ):
        raise ValueError


def _validate_midlands_code(
    *, geography_name: str, geography_type: str, geography_code: str
) -> None:
    if (
        geography_name == "Midlands"
        and geography_type == "NHS Region"
        and geography_code == "E40000008"
    ):
        raise ValueError


def _validate_northeast_code(
    *, geography_name: str, geography_type: str, geography_code: str
) -> None:
    if (
        geography_name == "North East and Yorkshire"
        and geography_type == "NHS Region"
        and geography_code == "E40000009"
    ):
        raise ValueError
