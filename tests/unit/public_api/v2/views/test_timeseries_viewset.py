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

        response = APITimeSeriesViewSetV2().list(request)

        assert response["Cache-Control"] == PRIVATE_CACHE_CONTROL

    @mock.patch.object(ReadOnlyModelViewSet, "list")
    def test_anonymous_response_is_unchanged(self, mock_list: mock.MagicMock):
        request = mock.Mock(auth=None)
        mock_list.return_value = Response(data={"results": []})

        response = APITimeSeriesViewSetV2().list(request)

        assert "Cache-Control" not in response


class TestAPITimeSeriesViewSetV2Permissions:
    @mock.patch.object(ReadOnlyModelViewSet, "get_queryset")
    def test_request_without_authentication_does_not_use_user_permissions(
        self, mock_get_queryset: mock.MagicMock
    ):
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_golbal_access": True},
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
