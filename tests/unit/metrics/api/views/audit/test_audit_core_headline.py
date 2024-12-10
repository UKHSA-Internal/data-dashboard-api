from unittest import mock
import pytest
from rest_framework import permissions

import config
from metrics.api.views.audit.audit_core_headline import AuditCoreHeadlineViewSet
from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet


class TestAuditCoreHeadlineViewSet:
    @mock.patch.object(permissions, "IsAuthenticated")
    def test_authentication_is_required_when_app_mode_cms_admin(
        self,
        spy_permissions_is_authenticated: mock.MagicMock,
    ):
        """
        Given the application is running with an APP_MODE of `CMS_ADMIN`
        When `get_permissions()` is called from the Core headline view set
        Then rest_frameworks's `IsAuthenticated()` will be called.
        """
        # Given
        config.APP_MODE = "CMS_ADMIN"
        audit_core_headline_viewset = AuditCoreHeadlineViewSet()

        # When
        audit_core_headline_viewset.get_permissions()

        # Then
        spy_permissions_is_authenticated.assert_called_once()
        config.APP_MODE = ""

    def test_sets_no_api_key_restrictions(self):
        """
        Given an instance of the `AuditCoreTimeseriesViewSet`
        When the `permission_classes` attribute is called
        Then an empty list is returned
        """
        # Given
        audit_core_headline_viewset = AuditCoreHeadlineViewSet()

        # When
        permission_classes = audit_core_headline_viewset.permission_classes

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
        Given an instance of the `AuditCoreHeadlineViewSet`
        When the `allowed_methods` attribute is called
        Then excluded HTTP methods are not in the returned list
        """
        # Given
        audit_core_headline_view = AuditCoreHeadlineViewSet()

        # When
        allowed_methods: list[str] = audit_core_headline_view.allowed_methods

        # Then
        assert excluded_http_methods not in allowed_methods
