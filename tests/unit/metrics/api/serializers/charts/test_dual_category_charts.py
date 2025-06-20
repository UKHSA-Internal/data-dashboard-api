import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.charts.dual_category_charts import (
    DualCategoryChartSegmentSerializer,
)
from metrics.domain.charts import colour_scheme


class TestDualCategoryChartSegmentSerializer:
    # Success cases
    def test_validates_successfully_with_all_required_fields(self):
        """
        Given a valid payload containing all required fields
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_9_DEEP_PLUM.name,
            "label": "0 to 4 years",
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_validates_successfully_with_single_primary_field_value(self):
        """
        Given a valid payload containing a single primary field value
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_10_PINK.name,
            "label": "0 to 4 years",
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    @pytest.mark.parametrize(
        "valid_colour_choice", colour_scheme.RGBAChartLineColours.choices()
    )
    def test_validates_successfully_with_all_valid_colour_choices(
        self, valid_colour_choice: tuple[str, str]
    ):
        """
        Given a valid payload containing each valid colour choice
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        colour_value: str = valid_colour_choice[0]
        valid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_value,
            "label": "0 to 4 years",
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid
        assert serializer.validated_data["colour"] == colour_value

    def test_validated_data_contains_correct_values(self):
        """
        Given a valid payload passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then the validated_data contains the correct values
        """
        # Given
        primary_values = ["m", "f"]
        secondary_field_value = "00-04"
        colour = colour_scheme.RGBAChartLineColours.COLOUR_4_ORANGE.name
        label = "0 to 4 years"

        valid_data_payload = {
            "secondary_field_value": secondary_field_value,
            "colour": colour,
            "label": label,
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid
        assert (
            serializer.validated_data["secondary_field_value"] == secondary_field_value
        )
        assert serializer.validated_data["colour"] == colour
        assert serializer.validated_data["label"] == label

    # Failure cases
    @pytest.mark.parametrize(
        "missing_field",
        [
            "secondary_field_value",
            "colour",
        ],
    )
    def test_invalid_when_required_field_is_missing(self, missing_field: str):
        """
        Given a payload missing a required field
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        complete_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_12_BLUE.name,
            "label": "0 to 4 years",
        }
        incomplete_payload = {
            k: v for k, v in complete_payload.items() if k != missing_field
        }

        serializer = DualCategoryChartSegmentSerializer(data=incomplete_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_when_secondary_field_value_is_empty_string(self):
        """
        Given a payload where secondary_field_value is an empty string
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        invalid_data_payload = {
            "secondary_field_value": "",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_11_KHAKI.name,
            "label": "Test Label",
        }

        serializer = DualCategoryChartSegmentSerializer(data=invalid_data_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_label_is_still_deemed_valid(self):
        """
        Given a payload where label is an empty string
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        invalid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_3_DARK_PINK.name,
            "label": "",
        }

        serializer = DualCategoryChartSegmentSerializer(data=invalid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid(raise_exception=True)

        # Then
        assert is_serializer_valid
