from unittest import mock

import pytest
from wagtail.blocks import StructBlock, StructBlockValidationError, StructValue

from cms.dynamic_content.global_filter.filter_types import DataFilters


class TestDataFilters:
    @property
    def valid_payload(self) -> dict:
        return {
            "data_filters": [],
            "categories_to_group_by": [
                {"type": "category", "value": {"data_category": "stratum"}},
                {"type": "category", "value": {"data_category": "topic"}},
            ],
        }

    @mock.patch.object(StructBlock, "clean")
    def test_clean_passes_with_valid_payload(
        self,
        mocked_super_clean: mock.MagicMock,
    ):
        """
        Given a `DataFilters` object with a valid payload
        When the `clean()` method is called
        Then no error should be raised
        """
        # Given
        data_filters = DataFilters()
        value: StructValue = data_filters.to_python(value=self.valid_payload)

        # When
        data_filters.clean(value=value)

        # Then
        mocked_super_clean.assert_called_once_with(value=value)

    def test_clean_raises_error_with_duplicate_selected_categories(self):
        """
        Given a `DataFilters` object with an invalid payload
            which contains duplicate selected categories
        When the `clean()` method is called
        Then an error should be raised
        """
        # Given
        invalid_payload = {**self.valid_payload}
        invalid_payload["categories_to_group_by"][0]["value"]["data_category"] = "topic"
        invalid_payload["categories_to_group_by"][1]["value"]["data_category"] = "topic"
        data_filters = DataFilters()
        value: StructValue = data_filters.to_python(value=invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as error:
            data_filters.clean(value=value)

        expected_error_message = (
            "The category of `topic` has been selected multiple times."
        )
        assert (
            error.value.block_errors["categories_to_group_by"].message
            == expected_error_message
        )
