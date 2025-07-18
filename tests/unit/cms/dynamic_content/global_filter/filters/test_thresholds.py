from unittest import mock

import pytest
from decimal import Decimal
from wagtail.blocks import (
    StructBlockValidationError,
    StructBlock,
    StructValue,
    StreamValue,
)

from cms.dynamic_content.global_filter.filter_types.thresholds import (
    ThresholdFilterElement,
    ThresholdsFilter,
)
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
        Given a `ThresholdFilterElement` with an otherwise valid payload
            but the `boundary_minimum_value` is greater than the `boundary_maximum_value`
        When `clean()` is called
        Then a `StructBlockValidationError` should be raised
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


class TestThresholdsFilter:
    @property
    def valid_payload(self) -> dict[str, list[dict[str, str]]]:
        return {
            "thresholds": [
                {
                    "type": "threshold",
                    "value": {
                        "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                        "label": "Level of coverage:",
                        "boundary_minimum_value": "0.00",
                        "boundary_maximum_value": "1.00",
                    },
                }
            ]
        }

    def test_clean_passes_with_valid_payload(self):
        """
        Given a `ThresholdsFilter` with a valid payload
        When the `clean()` method is called
        Then no error should be raised
        """
        # Given
        thresholds_filter = ThresholdsFilter()
        value: StructValue = thresholds_filter.to_python(value=self.valid_payload)

        # When
        result: StructValue = thresholds_filter.clean(value=value)

        # Then
        thresholds: StreamValue = result["thresholds"]
        first_threshold: StructValue = thresholds[0].value
        assert first_threshold["colour"] == RGBAChartLineColours.COLOUR_4_ORANGE.name
        assert first_threshold["label"] == "Level of coverage:"
        assert first_threshold["boundary_minimum_value"] == Decimal("0.00")
        assert first_threshold["boundary_maximum_value"] == Decimal("1.00")

    @pytest.mark.parametrize(
        "boundary_minimum_value, boundary_maximum_value",
        (
            ["0.5", "2.0"],
            ["1.0", "2.0"],
        ),
    )
    def test_clean_raises_validation_error_with_incorrect_boundary_values_across_thresholds(
        self, boundary_minimum_value: str, boundary_maximum_value: str
    ):
        """
        Given a `ThresholdsFilter` with an otherwise valid payload
            but the boundaries of the thresholds intersect each other
        When `clean()` is called
        Then a `StructBlockValidationError` should be raised
        """
        # Given
        invalid_payload = self.valid_payload.copy()
        invalid_payload["thresholds"].append(
            {
                "type": "threshold",
                "value": {
                    "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                    "label": "Level of coverage:",
                    "boundary_minimum_value": boundary_minimum_value,
                    "boundary_maximum_value": boundary_maximum_value,
                },
            }
        )
        thresholds_filter = ThresholdsFilter()
        value: StructValue = thresholds_filter.to_python(value=invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as exc_info:
            thresholds_filter.clean(value=value)

        block_errors = exc_info.value.block_errors
        assert (
            block_errors["thresholds"].message
            == f"Threshold No. 1's maximum value ({1.0}) must be less than threshold No. 2's minimum value ({boundary_minimum_value}) to maintain sequence order"
        )

    @mock.patch.object(StructBlock, "clean")
    def test_clean_calls_parent_clean(self, mocked_super_clean: mock.MagicMock):
        """
        Given a `ThresholdsFilter` with a valid payload
        When the `clean()` method is called
        Then the parent `clean()` method should be called
        """
        # Given
        thresholds_filter = ThresholdsFilter()
        value: StructValue = thresholds_filter.to_python(value=self.valid_payload)

        # When
        thresholds_filter.clean(value=value)

        # Then
        mocked_super_clean.assert_called_once_with(value=value)
