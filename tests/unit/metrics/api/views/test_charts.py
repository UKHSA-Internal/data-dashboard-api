from rest_framework import permissions

from metrics.api.views import ChartsView


class TestChartsView:
    def test_authentication_is_required(self):
        """
        Given a `ChartsView` object
        When `get_permission()` is called
        Then there is a permissions restriction of `IsAuthenticated`
        """
        # Given
        audit_core_timeseries_viewset = ChartsView()

        # When
        permissions_on_view = audit_core_timeseries_viewset.get_permissions()

        # Then
        assert type(permissions_on_view[0]) is permissions.IsAuthenticated
