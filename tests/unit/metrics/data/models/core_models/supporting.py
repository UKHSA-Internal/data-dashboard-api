from tests.fakes.models.metrics.geography import FakeGeography


def test_geography_model():
    """Tests that the geography_code field is available on geography model.

    Returns:
        None
    """
    # Given
    geography_code = "E450000012"

    # When
    geography_model = FakeGeography(geography_code=geography_code)

    # Then
    assert geography_model.geography_code == geography_code
