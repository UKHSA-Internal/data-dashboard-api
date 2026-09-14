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
