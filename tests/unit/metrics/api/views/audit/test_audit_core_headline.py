from unittest import mock
import pytest

from metrics.api.views.audit.audit_core_headline import AuditCoreHeadlineViewSet
from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet


class TestAuditCoreHeadlineViewSet:
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
