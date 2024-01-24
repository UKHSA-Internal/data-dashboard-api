import pytest

from public_api.views.base import BaseNestedAPITimeSeriesView


class TestBaseNestedAPITimeSeriesView:
    def test_raises_error_for_lookup_field_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `lookup_field` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesView()

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
        base_view = BaseNestedAPITimeSeriesView()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.serializer_class
