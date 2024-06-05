from unittest import mock
from http import HTTPStatus
from django.test import RequestFactory
import pytest
from rest_framework.response import Response
from django.urls import reverse
from rest_framework.test import APIClient

from metrics.api.serializers.geographies_alerts import GeographiesForAlertsSerializer
from metrics.api.views.alerts import BaseAlertViewSet


class InvalidMetricExtendedBaseAlertViewSet(BaseAlertViewSet):
    @property
    def topic_name(self) -> str:
        return "topic_name"


class InvalidTopicExtendedBaseAlertViewSet(BaseAlertViewSet):
    @property
    def metric_name(self) -> str:
        return "metric_name"


class TestHeatAlertsView:
    @property
    def path(self) -> str:
        return reverse("heat-alerts-list")

    @pytest.mark.django_db
    def test_list_returns_correct_response(self):
        """
        Given a valid request to the `alerts` endpoint
        When the `GET /api/alerts/v1/heat` endpoint is hit.
        Then the expected response is returned.
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.django_db
    @mock.patch.object(GeographiesForAlertsSerializer, "data")
    @mock.patch.object(GeographiesForAlertsSerializer, "is_valid")
    def test_retrieve_returns_correct_response(
        self, mock_is_valid: mock.Mock(), mock_data: mock.Mock()
    ):
        """
        Given a valid request `alerts` retrieve action endpoint
        When the `GET /api/alerts/v1/heat/{geography_code}` endpoint is hit.
        Then the correct response is returned.
        """
        # Given
        client = APIClient()
        path = f"{self.path}/E12000001"
        mock_data.return_value = [("E12000001", "North East")]
        mock_is_valid.return_value = True

        # When
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_retrieve_returns_400_response(
        self,
    ):
        """
        Given an invalid request to the `alerts` retrieve action endpoint
        When the `GET /api/alerts/v1/heat{geography_code}` endpoint is hit.
        Then a 400 Bad Request is returned.
        """
        # Given
        client = APIClient()
        path = f"{self.path}/invalid-code"

        # When
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestColdAlertsView:
    @property
    def path(self) -> str:
        return reverse("cold-alerts-list")

    @pytest.mark.django_db
    def test_list_returns_correct_response(self):
        """
        Given a valid request to the `alerts` endpoint
        When the `GET /api/alerts/v1/cold` endpoint is hit.
        Then the expected response is returned.
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.django_db
    @mock.patch.object(GeographiesForAlertsSerializer, "data")
    @mock.patch.object(GeographiesForAlertsSerializer, "is_valid")
    def test_retrieve_returns_correct_response(
        self, mock_is_valid: mock.MagicMock, mock_data: mock.MagicMock
    ):
        """
        Given a valid request `alerts` retrieve action endpoint
        When the `GET /api/alerts/v1/cold/{geography_code}` endpoint is hit.
        Then the correct response is returned.
        """
        # Given
        client = APIClient()
        path = f"{self.path}/E12000001"
        mock_data.return_value = [("E12000001", "North East")]
        mock_is_valid.return_value = True

        # When
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_retrieve_returns_400_response(
        self,
    ):
        """
        Given an invalid request to the `alerts` retrieve action endpoint
        When the `GET /api/alerts/v1/cold/{geography_code}` endpoint is hit.
        Then a 400 Bad Request is returned.
        """
        # Given
        client = APIClient()
        path = f"{self.path}/invalid-code"

        # When
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestBaseAlertsView:
    @pytest.mark.django_db
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

    @pytest.mark.django_db
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
