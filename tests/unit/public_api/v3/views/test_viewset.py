from unittest import mock
from django.db import models

import pytest

from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.version.v3.views.base import PRIVATE_CACHE_CONTROL
from public_api.version.v3.views.viewset import APIViewSetV3


class TestAPITimeSeriesViewSetV3CacheControl:
    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_authenticated_response_is_private(self, mock_list: mock.MagicMock):
        request = mock.Mock(auth="valid-jwt")
        mock_list.return_value = Response(data={"results": []})

        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=True,
        ):
            response = APIViewSetV3().list(request)

        assert response["Cache-Control"] == PRIVATE_CACHE_CONTROL

    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_anonymous_response_is_unchanged(self, mock_list: mock.MagicMock):
        request = mock.Mock(auth=None)
        mock_list.return_value = Response(data={"results": []})

        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=True,
        ):
            response = APIViewSetV3().list(request)

        assert "Cache-Control" not in response

    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_response_is_unchanged_when_authentication_is_disabled(
        self, mock_list: mock.MagicMock
    ):
        request = mock.Mock(auth="valid_jwt")
        mock_list.return_value = Response(data={"results": []})

        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=False,
        ):
            response = APIViewSetV3().list(request)

        assert "Cache-Control" not in response


class TestAPITimeSeriesViewSetV3Permissions:
    @pytest.mark.parametrize(
        "api_model",
        [
            MetricsPublicAPIInterface.get_api_timeseries_model(),
            MetricsPublicAPIInterface.get_api_headline_model(),
        ],
    )
    def test_request_without_authentication_does_not_use_user_permissions(
        self, api_model: models.Model
    ):
        # This isn't a scenario that could happen but tested anyway to prevent it
        # from creeping in
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        with mock.patch.object(api_model.objects, "get_queryset") as mock_get_queryset:
            queryset = mock_get_queryset.return_value
            view = APIViewSetV3(api_model=api_model)
            view.request = mock.Mock(
                auth=None,
                user=mock.Mock(permission_sets=permission_sets),
            )
            view.kwargs = {
                "theme": "theme",
                "sub_theme": "sub_theme",
                "topic": "topic",
                "geography_type": "geography-type",
                "geography": "geography",
                "metric": "metric",
            }

            with mock.patch(
                "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
                return_value=True,
            ):
                view.get_queryset()

            queryset.filter_for_list_view.assert_called_once_with(
                theme="theme",
                sub_theme="sub_theme",
                topic="topic",
                geography_type="geography-type",
                geography="geography",
                metric="metric",
                permission_sets=None,
            )

    @pytest.mark.parametrize(
        "api_model",
        [
            MetricsPublicAPIInterface.get_api_timeseries_model(),
            MetricsPublicAPIInterface.get_api_headline_model(),
        ],
    )
    def test_request_does_not_use_permissions_when_authentication_is_disabled(
        self, api_model: models.Model
    ):
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        with mock.patch.object(api_model.objects, "get_queryset") as mock_get_queryset:
            queryset = mock_get_queryset.return_value
            view = APIViewSetV3(api_model=api_model)
            view.request = mock.Mock(
                auth=None,
                user=mock.Mock(permission_sets=permission_sets),
            )
            view.kwargs = {
                "theme": "theme",
                "sub_theme": "sub_theme",
                "topic": "topic",
                "geography_type": "geography-type",
                "geography": "geography",
                "metric": "metric",
            }

            with mock.patch(
                "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
                return_value=False,
            ):
                view.get_queryset()

            queryset.filter_for_list_view.assert_called_once_with(
                theme="theme",
                sub_theme="sub_theme",
                topic="topic",
                geography_type="geography-type",
                geography="geography",
                metric="metric",
                permission_sets=None,
            )
