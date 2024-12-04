from unittest import mock
import pytest

from metrics.api.views.audit.audit_api_timeseries import AuditAPITimeSeriesViewSet
from metrics.data.managers.api_models.time_series import APITimeSeriesQuerySet


class TestAuditAPITimeseriesViewSet:
    def test_sets_no_api_key_restrictions(self):
        """
        Given an instance of the `AuditAPITimeseriesViewSet`
        When the `permission_classes` attribute is called
        Then an empty list is returned
        """
        # Given
        audit_api_timeseries_viewset = AuditAPITimeSeriesViewSet()

        # When
        permission_classes = audit_api_timeseries_viewset.permission_classes

        # Then
        assert permission_classes == []

    @pytest.mark.parametrize("excluded_http_method", ["POST", "PUT", "PATCH", "DELETE"])
    def test_allowed_http_methods_excludes_other_methods(
        self,
        excluded_http_method: str,
    ):
        """
        Given an instance of the `AuditAPITimeseriesViewSet`
        When the `allowed_methods` attribute is called
        Then excluded HTTP methods are not in the returned list
        """
        # Given
        audit_api_timeseries_view = AuditAPITimeSeriesViewSet()

        # When
        allowed_methods: list[str] = audit_api_timeseries_view.allowed_methods

        # Then
        assert excluded_http_method not in allowed_methods
