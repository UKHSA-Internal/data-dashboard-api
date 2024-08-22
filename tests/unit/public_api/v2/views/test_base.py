import pytest

from public_api.version_02.views.base import BaseNestedAPITimeSeriesViewV2


class TestBaseNestedAPITimeSeriesViewV2:
    def test_raises_error_for_lookup_field_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `lookup_field` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesViewV2()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.lookup_field

    def test_raises_error_for_serializer_class_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `serializer_class` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesViewV2()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.serializer_class
