from unittest import mock
import pytest
from rest_framework import permissions

import config
from metrics.api.views.audit.audit_core_timeseries import AuditCoreTimeseriesViewSet


class TestAuditCoreTimeseriesViewSet:
    @mock.patch.object(permissions, "IsAuthenticated")
    def test_authentication_is_required_when_app_mode_cms_admin(
        self,
        spy_permissions_is_authenticated: mock.MagicMock,
        monkeypatch,
    ):
        """
        Given the application is running with an APP_MODE of `CMS_ADMIN`
        When `get_permission()` is called from the Core timeseries view set
        Then rest_framework's `IsAuthenticated()` will be called.
        """
        # Given
        with monkeypatch.context() as m:
            m.setattr(target=config, name="APP_MODE", value="CMS_ADMIN")
            audit_core_timeseries_viewset = AuditCoreTimeseriesViewSet()

            # When
            audit_core_timeseries_viewset.get_permissions()

        # Then
        spy_permissions_is_authenticated.assert_called_once()

    def test_sets_no_api_key_restrictions(self):
        """
        Given an instance of the `AuditCoreTimeseriesViewSet`
        When the `permission_classes` attribute is called
        Then an empty list is returned
        """
        # Given
        audit_core_timeseries_viewset = AuditCoreTimeseriesViewSet()

        # When
        permission_classes = audit_core_timeseries_viewset.permission_classes

        # Then
        assert permission_classes == []

    @pytest.mark.parametrize(
        "excluded_http_methods", ["POST", "PUT", "PATCH", "DELETE"]
    )
    def test_allowed_http_methods_excludes_other_methods(
        self,
        excluded_http_methods: str,
    ):
        """
        Given an instance of the `AuditCoreTimeseriesViewSet`
        When the `allowed_methods` attribute is called
        Then excluded HTTP methods are not in the returned list
        """
        # Given
        audit_core_timeseries_view = AuditCoreTimeseriesViewSet()

        # When
        allowed_methods: list[str] = audit_core_timeseries_view.allowed_methods

        # Then
        assert excluded_http_methods not in allowed_methods
