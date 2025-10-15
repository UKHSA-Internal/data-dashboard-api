DEPRECATED_GEOGRAPHY_COMBINATION_ERROR_MESSAGE = "The given `geography`, `geography_type` and `geography_code` combination is deprecated."


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
    _deprecated_geography(
        geography_name=geography_name,
        geography_type=geography_type,
        geography_code=geography_code,
    )


DEPRECATED_GEOGRAPHIES: set[tuple[str, str, str]] = {
    ("Midlands", "NHS Region", "E40000008"),
    ("North East and Yorkshire", "NHS Region", "E40000009"),
    ("East of England", "NHS Region", "E40000007"),
    ("North West", "NHS Region", "E40000010"),
}


def _validate_st_helens_trust(*, geography_name: str, geography_type: str) -> None:
    if (
        geography_name == "St Helens and Knowsley Teaching Hospitals NHS Trust"
        and geography_type == "NHS Trust"
    ):
        error_message = f"The given `geography` of '{geography_name}' under the `geography_type` of '{geography_type}' is deprecated"
        raise ValueError(error_message)


def _deprecated_geography(
    *, geography_name: str, geography_type: str, geography_code: str
) -> None:
    is_deprecated: bool = (
        geography_name,
        geography_type,
        geography_code,
    ) in DEPRECATED_GEOGRAPHIES
    if is_deprecated:
        error_message = f"The given `geography` of '{geography_name}' under the `geography_type` of '{geography_type}' with the `geography_code` of '{geography_code}' is deprecated"
        raise ValueError(error_message)
