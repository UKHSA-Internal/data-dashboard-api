import pytest

from validation.deprecated_geographies import validate_deprecated_geographies


class TestDeprecatedGeographies:
    @pytest.mark.parametrize(
        "geography_name, geography_code, geography_type",
        [
            (
                "St Helens and Knowsley Teaching Hospitals NHS Trust",
                "E40000001",
                "NHS Trust",
            ),
            ("Midlands", "E40000008", "NHS Region"),
            ("North East and Yorkshire", "E40000009", "NHS Region"),
            ("East of England", "E40000007", "NHS Region"),
            ("North West", "E40000010", "NHS Region"),
        ],
    )
    def test_deprecated_geographies(
        self, geography_name, geography_code, geography_type
    ):
        """
        Given a deprecated geography
        When `validate_deprecated_geographies()` is called
        Then a `ValueError` is raised
        """
        with pytest.raises(ValueError):
            validate_deprecated_geographies(
                geography_name=geography_name,
                geography_code=geography_code,
                geography_type=geography_type,
            )
