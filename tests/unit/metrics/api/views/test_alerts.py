from unittest import mock
from django.urls import reverse

from django.test import RequestFactory

from metrics.api.views.alerts import BaseAlertViewSet
import pytest


class InvalidMetricExtendedBaseAlertViewSet(BaseAlertViewSet):
    @property
    def topic_name(self) -> str:
        return "topic_name"


class InvalidTopicExtendedBaseAlertViewSet(BaseAlertViewSet):
    @property
    def metric_name(self) -> str:
        return "metric_name"


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

    def test_raises_error_if_topic_name_not_implemented(self):
        """
        Given an instance of the `BaseAlertViewSet`
        When the `topic_name` is not implemented in the child class
        Then a `NotImplementedError` is raised.
        """
        # Given
        path = reverse("cold-alerts-list")
        fake_request = RequestFactory().get(path)
        fake_request.query_params = mock.MagicMock()
        extended_base_alert_view_set = InvalidTopicExtendedBaseAlertViewSet()

        # When / Then
        with pytest.raises(NotImplementedError):
            extended_base_alert_view_set.list(fake_request)

    def test_raises_error_if_metric_name_not_implemented(self):
        """
        Given an instance of the `BaseAlertViewSet`
        When the `metric_name` is not implemented in the child class
        Then a `NotImplementedError` is raised.
        """
        # Given
        path = reverse("cold-alerts-list")
        fake_request = RequestFactory().get(path)
        fake_request.query_params = mock.MagicMock()
        extended_base_alert_view_set = InvalidMetricExtendedBaseAlertViewSet()

        # When / Then
        with pytest.raises(NotImplementedError):
            extended_base_alert_view_set.list(fake_request)
