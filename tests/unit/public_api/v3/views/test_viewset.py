from unittest import mock
from django.db import models

import pytest

from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.version.v3.views.base import PRIVATE_CACHE_CONTROL
from public_api.version.v3.views.viewset import APIViewSetV3
from public_api.version.v3.serializers.serializers import (
    APITimeSeriesListSerializerv3,
    APIHeadlineListSerializerv3,
)


class TestAPIViewSetV3CacheControl:
    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_authenticated_response_is_private(self, mock_list: mock.MagicMock):
        """
        Given  a mocked requires with a valid jwt
        When the `list()` method is called with the mocked request
        Then the expected `Cache-Control` header is returned
        """
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
        """
        Given a mocked requires without a jwt
        When the `list()` method is called with the mocked request
        Then the `Cache-Control` header is not returned in the response
        """
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
        """
        Given a mocked requires with a valid-jwt
        AND `is_auth_enabled` is `False`
        When the `list()` method is called with the mocked request
        Then the `Cache-Control` header is not returned in the response
        """
        request = mock.Mock(auth="valid_jwt")
        mock_list.return_value = Response(data={"results": []})

        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=False,
        ):
            response = APIViewSetV3().list(request)

        assert "Cache-Control" not in response


class TestAPIViewSetV3Permissions:
    @pytest.mark.parametrize(
        "api_model, api_serializer_class, auth_enabled",
        [
            (
                MetricsPublicAPIInterface.get_api_timeseries_model(),
                APITimeSeriesListSerializerv3,
                True,
            ),
            (
                MetricsPublicAPIInterface.get_api_headline_model(),
                APIHeadlineListSerializerv3,
                True,
            ),
            (
                MetricsPublicAPIInterface.get_api_timeseries_model(),
                APITimeSeriesListSerializerv3,
                False,
            ),
            (
                MetricsPublicAPIInterface.get_api_headline_model(),
                APIHeadlineListSerializerv3,
                False,
            ),
        ],
    )
    def test_request_without_authentication_does_not_use_user_permissions(
        self,
        api_model: models.Model,
        api_serializer_class: (
            APITimeSeriesListSerializerv3 | APIHeadlineListSerializerv3
        ),
        auth_enabled: bool,
    ):
        """
        Given a mocked request without authentication token
        And empty `permission_sets`
        When the request is made with or without `is_auth_enabled` is `True`
        Then the `filter_for_list_view()` method is called without `permission_sets`

        Note:
            This isn't a scenario that could happen but tested anyway to prevent it
            from creeping in
        """
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        with mock.patch.object(api_model.objects, "get_queryset") as mock_get_queryset:
            queryset = mock_get_queryset.return_value
            view = APIViewSetV3(
                api_model=api_model, serializer_class=api_serializer_class
            )
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
                return_value=auth_enabled,
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
