import pytest
from pydantic_core._pydantic_core import ValidationError

from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.models.charts.segments import SegmentParameters


class TestSegmentParameters:
    @property
    def valid_primary_field_values(self) -> list[str]:
        return ["m", "f"]

    @property
    def valid_secondary_field_value(self) -> str:
        return "00-04"

    @property
    def valid_colour(self) -> str:
        return RGBAChartLineColours.COLOUR_1_DARK_BLUE.name

    @property
    def valid_label(self) -> str:
        return "0 to 4 years"

    def test_segment_parameters_creation_with_valid_data(self):
        """
        Given a valid payload
        When creating a `SegmentParameters` model
        Then the instance should be created successfully with correct values
        """
        # Given
        primary_field_values = self.valid_primary_field_values
        secondary_field_value = self.valid_secondary_field_value
        colour = self.valid_colour
        label = self.valid_label

        # When
        segment_params = SegmentParameters(
            primary_field_values=primary_field_values,
            secondary_field_value=secondary_field_value,
            colour=colour,
            label=label,
        )

        # Then
        assert segment_params.primary_field_values == self.valid_primary_field_values
        assert segment_params.secondary_field_value == self.valid_secondary_field_value
        assert segment_params.colour == self.valid_colour
        assert segment_params.label == self.valid_label

    def test_validates_for_no_label(self):
        """
        Given valid parameters with None as the label
        When creating a `SegmentParameters` model
        Then the instance should be created successfully
        """
        # Given
        primary_field_values = self.valid_primary_field_values
        secondary_field_value = self.valid_secondary_field_value
        colour = self.valid_colour
        label = None

        # When
        segment_params = SegmentParameters(
            primary_field_values=primary_field_values,
            secondary_field_value=secondary_field_value,
            colour=colour,
            label=label,
        )

        # Then
        assert segment_params.primary_field_values == self.valid_primary_field_values
        assert segment_params.secondary_field_value == self.valid_secondary_field_value
        assert segment_params.colour == self.valid_colour
        assert segment_params.label is None

    def test_raises_validation_error_for_missing_primary_field_values(self):
        """
        Given no `primary_field_values` parameter
        When creating a `SegmentParameters` model
        Then a `ValidationError` should be raised
        """
        # Given
        secondary_field_value = self.valid_secondary_field_value
        colour = self.valid_colour
        label = self.valid_label

        # When
        with pytest.raises(ValidationError) as error:
            SegmentParameters(
                secondary_field_value=secondary_field_value, colour=colour, label=label
            )

        # Then
        assert "primary_field_values" in str(error.value)

    def test_raises_validation_error_for_missing_secondary_field_value(self):
        """
        Given no `secondary_field_value` parameter
        When creating a `SegmentParameters` model
        Then a `ValidationError` should be raised
        """
        # Given
        primary_field_values = self.valid_primary_field_values
        colour = self.valid_colour
        label = self.valid_label

        # When
        with pytest.raises(ValidationError) as error:
            SegmentParameters(
                primary_field_values=primary_field_values, colour=colour, label=label
            )

        # Then
        assert "secondary_field_value" in str(error.value)

    def test_raises_validation_error_for_missing_colour(self):
        """
        Given no `colour` parameter
        When creating a `SegmentParameters` model
        Then a `ValidationError` should be raised
        """
        # Given
        primary_field_values = self.valid_primary_field_values
        secondary_field_value = self.valid_secondary_field_value
        label = self.valid_label

        # When
        with pytest.raises(ValidationError) as error:
            SegmentParameters(
                primary_field_values=primary_field_values,
                secondary_field_value=secondary_field_value,
                label=label,
            )

        # Then
        assert "colour" in str(error.value)

    def test_raises_validation_error_for_invalid_primary_field_values(self):
        """
        Given an invalid type for the `primary_field_values` parameter
        When creating a `SegmentParameters` model
        Then a `ValidationError` should be raised
        """
        # Given
        primary_field_values = "f"
        secondary_field_value = self.valid_secondary_field_value
        colour = self.valid_colour
        label = self.valid_label

        # When
        with pytest.raises(ValidationError) as error:
            SegmentParameters(
                primary_field_values=primary_field_values,
                secondary_field_value=secondary_field_value,
                colour=colour,
                label=label,
            )

        # Then
        assert "primary_field_values" in str(error.value)

    def test_raises_error_for_secondary_field_value_type(self):
        """
        Given an invalid type for the `secondary_field_value` parameter
        When creating a `SegmentParameters` model
        Then a `ValidationError` should be raised
        """
        # Given
        primary_field_values = self.valid_primary_field_values
        secondary_field_value = ["00-04"]
        colour = self.valid_colour
        label = self.valid_label

        # When
        with pytest.raises(ValidationError) as error:
            SegmentParameters(
                primary_field_values=primary_field_values,
                secondary_field_value=secondary_field_value,
                colour=colour,
                label=label,
            )

        # Then
        assert "secondary_field_value" in str(error.value)

    def test_colour_enum_property_returns_selected_colour(self):
        """
        Given a SegmentParameters instance with a valid colour
        When accessing `colour_enum` from the `SegmentParameters` instance
        Then it should return the corresponding RGBAChartLineColours enum
        """
        # Given
        segment_params = SegmentParameters(
            primary_field_values=self.valid_primary_field_values,
            secondary_field_value=self.valid_secondary_field_value,
            colour=RGBAChartLineColours.COLOUR_3_DARK_PINK.name,
            label=self.valid_label,
        )

        # When
        colour_enum = segment_params.colour_enum

        # Then
        assert colour_enum == RGBAChartLineColours.COLOUR_3_DARK_PINK

    @pytest.mark.parametrize("colour", [None, ""])
    def test_colour_enum_property_returns_dark_blue_as_default_colour(
        self, colour: None | str
    ):
        """
        Given a payload which does not specify the `colour` parameter
        When accessing `colour_enum` from the `SegmentParameters` instance
        Then `COLOUR_1_DARK_BLUE` is returned by default
        """
        # Given
        segment_params = SegmentParameters(
            primary_field_values=self.valid_primary_field_values,
            secondary_field_value=self.valid_secondary_field_value,
            colour=colour,
            label=self.valid_label,
        )

        # When
        colour_enum = segment_params.colour_enum

        # Then
        assert colour_enum == RGBAChartLineColours.COLOUR_1_DARK_BLUE
