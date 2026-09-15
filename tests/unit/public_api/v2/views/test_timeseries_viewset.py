from unittest import mock

from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from public_api.version_02.views.base import PRIVATE_CACHE_CONTROL
from public_api.version_02.views.timeseries_viewset import APITimeSeriesViewSetV2


class TestAPITimeSeriesViewSetV2CacheControl:
    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_authenticated_response_is_private(self, mock_list: mock.MagicMock):
        request = mock.Mock(auth="valid-jwt")
        mock_list.return_value = Response(data={"results": []})

        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=True,
        ):
            response = APITimeSeriesViewSetV2().list(request)

        assert response["Cache-Control"] == PRIVATE_CACHE_CONTROL

    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_anonymous_response_is_unchanged(self, mock_list: mock.MagicMock):
        request = mock.Mock(auth=None)
        mock_list.return_value = Response(data={"results": []})

        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=True,
        ):
            response = APITimeSeriesViewSetV2().list(request)

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
            response = APITimeSeriesViewSetV2().list(request)

        assert "Cache-Control" not in response


class TestAPITimeSeriesViewSetV2Permissions:
    @mock.patch.object(ReadOnlyModelViewSet, "get_queryset")
    def test_request_without_authentication_does_not_use_user_permissions(
        self, mock_get_queryset: mock.MagicMock
    ):
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        queryset = mock_get_queryset.return_value
        view = APITimeSeriesViewSetV2()
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

    @mock.patch.object(ReadOnlyModelViewSet, "get_queryset")
    def test_request_does_not_use_permissions_when_authentication_is_disabled(
        self, mock_get_queryset: mock.MagicMock
    ):
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        queryset = mock_get_queryset.return_value
        view = APITimeSeriesViewSetV2()
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
