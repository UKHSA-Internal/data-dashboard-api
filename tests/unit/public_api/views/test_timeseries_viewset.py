from unittest import mock

from rest_framework.viewsets import ReadOnlyModelViewSet

from public_api.views.timeseries_viewset import APITimeSeriesViewSet


class TestAPITimeSeriesViewSetPermissions:
    @mock.patch.object(ReadOnlyModelViewSet, "get_queryset")
    def test_request_without_authentication_does_not_use_user_permissions(
        self, mock_get_queryset: mock.MagicMock
    ):
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        queryset = mock_get_queryset.return_value
        view = APITimeSeriesViewSet()
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
