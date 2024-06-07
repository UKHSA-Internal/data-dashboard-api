from unittest import mock
import pytest

from metrics.api.views.alerts import BaseAlertViewSet, HeatAlertViewSet


class TestBaseAlertsView:
    def test_sets_no_api_key_restrictions(self):
        """
        Given an instance of the `BaseAlertViewSet`
        When the `permission_classes` attribute is called
        Then an empty list is returned
        """
        # Given
        base_alert_view = BaseAlertViewSet()

        # When
        permission_classess = base_alert_view.permission_classes

        # Then
        assert permission_classess == []
