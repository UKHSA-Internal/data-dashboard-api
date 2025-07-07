import datetime
from unittest import mock

import pytest
from decimal import Decimal
from wagtail.blocks import StructBlockValidationError, StructBlock

from cms.dynamic_content.global_filter.card import TimeRangeElement, TimeRangeBlock
from cms.dynamic_content.global_filter.filters import (
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
                    "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                    "label": "Level of coverage:",
                    "boundary_minimum_value": "0.00",
                    "boundary_maximum_value": "1.00",
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
        thresholds_filter = ThresholdsFilter(**self.valid_payload)

        # When
        result = thresholds_filter.clean(self.valid_payload)

        # Then
        thresholds = result["thresholds"]
        assert thresholds[0]["colour"] == RGBAChartLineColours.COLOUR_4_ORANGE.name
        assert thresholds[0]["label"] == "Level of coverage:"
        assert thresholds[0]["boundary_minimum_value"] == Decimal("0.00")
        assert thresholds[0]["boundary_maximum_value"] == Decimal("1.00")

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
                "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                "label": "Level of coverage:",
                "boundary_minimum_value": boundary_minimum_value,
                "boundary_maximum_value": boundary_maximum_value,
            }
        )
        thresholds_filter = ThresholdsFilter(**invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as exc_info:
            thresholds_filter.clean(invalid_payload)

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
        thresholds_filter = ThresholdsFilter(**self.valid_payload)

        # When
        thresholds_filter.clean(self.valid_payload)

        # Then
        mocked_super_clean.assert_called_once_with(value=self.valid_payload)


class TestTimeRangeElement:
    @property
    def valid_payload(self) -> dict[str, str | datetime.date]:
        return {
            "label": "Year selection:",
            "date_from": datetime.date(year=2025, month=1, day=10),
            "date_to": datetime.date(year=2025, month=1, day=11),
        }

    def test_clean_passes_with_valid_payload(self):
        """
        Given a `TimeRangeElement` with a valid payload
        When the `clean()` method is called
        Then no error should be raised
        """
        # Given
        valid_payload = self.valid_payload
        time_range_element = TimeRangeElement(**valid_payload)

        # When
        result = time_range_element.clean(valid_payload)

        # Then
        assert result["label"] == valid_payload["label"]
        assert result["date_from"] == valid_payload["date_from"]
        assert result["date_to"] == valid_payload["date_to"]

    def test_clean_raises_validation_error_with_incorrect_boundary_values(self):
        """
        Given a `TimeRangeElement` with an otherwise valid payload
            but the dates are not in chronological order
        When the `clean()` method is called
        Then a `StructBlockValidationError` should be raised
        """
        # Given
        invalid_payload = self.valid_payload.copy()
        invalid_payload["date_from"] = datetime.date(year=2025, month=1, day=27)
        threshold_filter_element = TimeRangeElement(**invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as exc_info:
            threshold_filter_element.clean(invalid_payload)

        block_errors = exc_info.value.block_errors
        assert (
            block_errors["date_from"].message
            == "The `date_from` must be earlier than the `date_to`"
        )

    @mock.patch.object(StructBlock, "clean")
    def test_clean_calls_parent_clean(self, mocked_super_clean: mock.MagicMock):
        """
        Given a `TimeRangeElement` with a valid payload
        When the `clean()` method is called
        Then the parent `clean()` method should be called
        """
        # Given
        valid_payload = self.valid_payload
        time_range_element = TimeRangeElement(**valid_payload)

        # When
        time_range_element.clean(valid_payload)

        # Then
        mocked_super_clean.assert_called_once_with(value=valid_payload)


class TestTimeRangeBlock:
    @property
    def valid_payload(self) -> dict[str, list[dict[str, str]]]:
        return {
            "title": "Time selection",
            "time_periods": [
                {
                    "label": "10th Jan - 13th Jan",
                    "date_from": "2025-01-10",
                    "date_to": "2025-01-13",
                }
            ],
        }

    def test_clean_passes_with_valid_payload(self):
        """
        Given a `TimeRangeBlock` with a valid payload
        When the `clean()` method is called
        Then no error should be raised
        """
        # Given
        valid_payload = self.valid_payload
        time_range_block = TimeRangeBlock(**valid_payload)

        # When
        result = time_range_block.clean(valid_payload)

        # Then
        time_periods = result["time_periods"]
        assert time_periods[0]["label"] == "10th Jan - 13th Jan"
        assert time_periods[0]["date_from"] == datetime.date.fromisoformat(
            valid_payload["time_periods"][0]["date_from"]
        )
        assert time_periods[0]["date_to"] == datetime.date.fromisoformat(
            valid_payload["time_periods"][0]["date_to"]
        )

    @pytest.mark.parametrize(
        "date_from, date_to",
        (
            ["2025-01-12", "2025-01-20"],
            ["2025-01-13", "2025-01-20"],
        ),
    )
    def test_clean_raises_validation_error_with_dates_across_time_periods(
        self, date_from: datetime.date, date_to: datetime.date
    ):
        """
        Given a `TimeRangeBlock` with an otherwise valid payload
            but the dates of the time periods are not in order
            1 day after the other
        When `clean()` is called
        Then a `StructBlockValidationError` should be raised
        """
        # Given
        invalid_payload = self.valid_payload.copy()
        invalid_payload["time_periods"].append(
            {
                "label": "Incorrect date range",
                "date_from": date_from,
                "date_to": date_to,
            }
        )
        time_range_block = TimeRangeBlock(**invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as exc_info:
            time_range_block.clean(invalid_payload)

        block_errors = exc_info.value.block_errors
        assert (
            block_errors["time_periods"].message
            == f"Time period No. 2's `date_from` ({date_from}) must be 1 day after time period No. 1 `date_to`(2025-01-13) to maintain sequence order"
        )

    @mock.patch.object(StructBlock, "clean")
    def test_clean_calls_parent_clean(self, mocked_super_clean: mock.MagicMock):
        """
        Given a `TimeRangeBlock` with a valid payload
        When the `clean()` method is called
        Then the parent `clean()` method should be called
        """
        # Given
        valid_payload = self.valid_payload
        time_range_block = TimeRangeBlock(**valid_payload)

        # When
        time_range_block.clean(valid_payload)

        # Then
        mocked_super_clean.assert_called_once_with(value=valid_payload)
