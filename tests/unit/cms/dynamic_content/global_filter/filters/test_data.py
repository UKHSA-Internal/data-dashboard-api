from unittest import mock

import pytest
from wagtail.blocks import StructBlock, StructBlockValidationError

from cms.dynamic_content.global_filter.filter_types import DataFilters


class TestDataFilters:
    @property
    def valid_payload(self) -> dict[str, list[dict[str, str]]]:
        return {
            "data_filters": [],
            "categories_to_group_by": [
                {"data_category": "stratum"},
                {"data_category": "topic"},
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
        data_filters = DataFilters(**self.valid_payload)

        # When
        data_filters.clean(self.valid_payload)

        # Then
        mocked_super_clean.assert_called_once_with(value=self.valid_payload)

    def test_clean_raises_error_with_duplicate_selected_categories(self):
        """
        Given a `DataFilters` object with an invalid payload
            which contains duplicate selected categories
        When the `clean()` method is called
        Then an error should be raised
        """
        # Given
        invalid_payload = {**self.valid_payload}
        invalid_payload["categories_to_group_by"][0]["data_category"] = "topic"
        invalid_payload["categories_to_group_by"][1]["data_category"] = "topic"
        data_filters = DataFilters(**invalid_payload)

        # When / Then
        with pytest.raises(StructBlockValidationError) as error:
            data_filters.clean(invalid_payload)

        expected_error_message = (
            "The category `topic` has been selected multiple times."
        )
        assert (
            error.value.block_errors["categories_to_group_by"].message
            == expected_error_message
        )
