from unittest import mock
from django.core.exceptions import ValidationError

import pytest
from wagtail.blocks import StructBlock, StructValue, StructBlockValidationError
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from cms.metrics_interface import MetricsAPIInterface

from cms.dynamic_content.global_filter.filter_types import GeographyFilter


class TestGeographyFilter:
    @property
    def valid_payload(self) -> dict[str, str]:
        return {
            "geography_types": [
                {
                    "type": "geography_filter",
                    "value": {
                        "label": "Region:",
                        "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                        "geography_type": "UKHSA Region",
                    },
                },
                {
                    "type": "geography_filter",
                    "value": {
                        "label": "Country:",
                        "colour": RGBAChartLineColours.COLOUR_2_TURQUOISE.name,
                        "geography_type": "Nation",
                    },
                },
            ]
        }

    @mock.patch.object(StructBlock, "clean")
    def test_clean_passes_with_valid_payload(
        self,
        mocked_super_clean: mock.MagicMock,
    ):
        """
        Given a `GeographyFilter` with a valid payload
        When the `clean()` method is called
        Then no error should be raised
        """
        # Given
        geography_filter = GeographyFilter()
        value: StructValue = geography_filter.to_python(value=self.valid_payload)

        # When
        geography_filter.clean(value=value)

        # Then
        mocked_super_clean.assert_called_once_with(value=value)

    @mock.patch.object(MetricsAPIInterface, "get_all_geography_type_names")
    def test_clean_raises_error_with_invalid_geography_types(
        self, mocked_get_all_geography_type_names: mock.MagicMock
    ):
        """
        Given a `GeographyFilter` with an invalid payload
        When the `clean()` method is called
        Then an error should be raised
        """
        # Given
        mocked_get_all_geography_type_names.return_value = [
            "Nation",
            "Lower Tier Local Authority",
        ]
        geography_filter = GeographyFilter()
        invalid_payload = self.valid_payload.copy()
        invalid_payload["geography_types"][0]["value"]["geography_type"] = "England"
        value: StructValue = geography_filter.to_python(value=invalid_payload)

        # When / Then
        with pytest.raises(ValidationError):
            geography_filter.clean(value=value)

    @mock.patch.object(MetricsAPIInterface, "get_all_geography_type_names")
    @pytest.mark.parametrize(
        "field_to_duplicate",
        [
            "colour",
            "label",
            "geography_type",
        ],
    )
    def test_raises_validation_error_for_duplicated_fields(
        self,
        mocked_get_all_geography_type_names: mock.MagicMock,
        field_to_duplicate: str,
    ):
        """
        Given a payload containing duplicated fields
            across different geography filters
        When the `clean()` method is called from the `GeographyFilter`
        Then a `StructBlockValidationError` is raised
        """
        # Given
        mocked_get_all_geography_type_names.return_value = ["Nation", "UKHSA Region"]
        invalid_payload = self.valid_payload.copy()
        field_to_copy_between_filters = self.valid_payload["geography_types"][0][
            "value"
        ][field_to_duplicate]

        invalid_payload["geography_types"][1]["value"][
            field_to_duplicate
        ] = field_to_copy_between_filters
        geography_filter = GeographyFilter()
        value: StructValue = geography_filter.to_python(value=invalid_payload)

        # When
        with pytest.raises(StructBlockValidationError) as error:
            geography_filter.clean(value=value)

        # Then
        expected_error_message = f"The {field_to_duplicate} of `{field_to_copy_between_filters}` has been used multiple times. This must be unique, please review your selection. "
        assert (
            error.value.block_errors[field_to_duplicate].message
            == expected_error_message
        )
