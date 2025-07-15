from unittest import mock
from django.core.exceptions import ValidationError

import pytest
from wagtail.blocks import StructBlock
from metrics.domain.charts.colour_scheme import RGBAChartLineColours

from cms.dynamic_content.global_filter.filter_types import GeographyFilter


class TestGeographyFilter:
    @property
    def valid_payload(self) -> dict[str, str]:
        return {
            "geography_types": [
                {
                    "label": "Region:",
                    "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                    "geography_type": "UKHSA Region",
                },
                {
                    "label": "Nation:",
                    "colour": RGBAChartLineColours.COLOUR_2_TURQUOISE.name,
                    "geography_type": "England",
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
        geography_filter = GeographyFilter(**self.valid_payload)

        # When
        geography_filter.clean(self.valid_payload)

        # Then
        mocked_super_clean.assert_called_once_with(value=self.valid_payload)

    def test_clean_raises_error_with_invalid_geography_types(self):
        """
        Given a `GeographyFilter` with an invalid payload
        When the `clean()` method is called
        Then an error should be raised
        """
        # Given
        invalid_payload = {**self.valid_payload}
        invalid_payload["geography_types"][0]["geography_type"] = "England"
        geography_filter = GeographyFilter(**invalid_payload)

        # When / Then
        with pytest.raises(ValidationError):
            geography_filter.clean(invalid_payload)

    def test_clean_raises_error_with_invalid_colours(self):
        """
        Given a `GeographyFilter` with an invalid payload
        When the `clean()` method is called
        Then an error should be raised
        """
        # Given
        invalid_payload = {**self.valid_payload}
        invalid_payload["geography_types"][0][
            "colour"
        ] = RGBAChartLineColours.COLOUR_2_TURQUOISE.name
        geography_filter = GeographyFilter(**invalid_payload)

        # When / Then
        with pytest.raises(ValidationError):
            geography_filter.clean(invalid_payload)
