from unittest import mock

import pytest
from decimal import Decimal
from wagtail.blocks import StructBlockValidationError, StructBlock

from cms.dynamic_content.global_filter.filters import ThresholdFilterElement
from metrics.domain.charts.colour_scheme import RGBAChartLineColours


class TestThresholdFilterElement:
    @property
    def valid_payload(self) -> dict[str, str]:
        return {
            "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
            "label": "Level of coverage:",
            "boundary_minimum_value": "0.00",
            "boundary_maximum_value": "1.00",
        }

    def test_clean_passes_with_valid_payload(self):
        """
        Given a `ThresholdFilterElement` with a valid payload
        When the `clean()` method is called
        Then no error should be raised
        """
        # Given
        threshold_filter_element = ThresholdFilterElement(**self.valid_payload)

        # When
        result = threshold_filter_element.clean(self.valid_payload)

        # Then
        assert result["colour"] == RGBAChartLineColours.COLOUR_4_ORANGE.name
        assert result["label"] == "Level of coverage:"
        assert result["boundary_minimum_value"] == Decimal("0.00")
        assert result["boundary_maximum_value"] == Decimal("1.00")

    @pytest.mark.parametrize(
        "boundary_minimum_value, boundary_maximum_value",
        (
            ["2.00", "1.00"],
            ["1.00", "2.00"],
        ),
    )
    def test_clean_raises_validation_error_with_incorrect_boundary_values(
        self, boundary_minimum_value: str, boundary_maximum_value: str
    ):
        """
        Given a ThresholdFilterElement with an otherwise valid payload
            but the `boundary_minimum_value` is greater than the `boundary_maximum_value`
        When clean() is called
        Then StructBlockValidationError should be raised
        """
        # Given
        invalid_payload = self.valid_payload.copy()
        invalid_payload["boundary_minimum_value"] = "2.00"
        threshold_filter_element = ThresholdFilterElement(**invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as exc_info:
            threshold_filter_element.clean(invalid_payload)

        block_errors = exc_info.value.block_errors
        assert (
            block_errors["boundary_maximum_value"].message
            == "The `boundary_maximum_value` must be greater than the `boundary_minimum_value`"
        )
        assert (
            block_errors["boundary_minimum_value"].message
            == "The `boundary_minimum_value` must be less than the `boundary_maximum_value`"
        )

    @mock.patch.object(StructBlock, "clean")
    def test_clean_calls_parent_clean(self, mocked_super_clean: mock.MagicMock):
        """
        Given a `ThresholdFilterElement` with a valid payload
        When the `clean()` method is called
        Then the parent `clean()` method should be called
        """
        # Given
        threshold_filter_element = ThresholdFilterElement(**self.valid_payload)

        # When
        threshold_filter_element.clean(self.valid_payload)

        # Then
        mocked_super_clean.assert_called_once_with(value=self.valid_payload)
