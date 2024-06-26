from metrics.data.models.core_models.supporting import (
    GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT,
)
from tests.fakes.models.metrics.geography import FakeGeography


class TestGeography:
    geography_code = "E45000001"

    def test_geography_code_exists(self):
        """
        Given I have a valid geography code.
        When I initialise a new instance of the geography model passing the geography_code.
        Then the value will be assigned to the model's geography_code field.
        """
        # Given
        geography_code = self.geography_code

        # When
        geography_model = FakeGeography(geography_code=geography_code)

        # Then
        assert geography_model.geography_code == geography_code

    def test_geography_code_max_length(self):
        """
        Given I have a geography_code and a max_length value
        When I initialise a new instance of the geography model passing in the geography code.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        geography_code = self.geography_code
        max_length_constraint = GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT

        # When
        geography_model = FakeGeography(geography_code=geography_code)
        geography_code_field = next(
            field
            for field in geography_model._meta.concrete_fields
            if field.attname == "geography_code"
        )

        # Then
        assert geography_code_field.max_length == max_length_constraint
