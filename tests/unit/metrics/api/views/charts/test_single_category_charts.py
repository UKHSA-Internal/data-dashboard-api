from _pytest.monkeypatch import MonkeyPatch
from rest_framework import permissions

import config
from metrics.api.views import ChartsView


class TestChartsView:
    def test_authentication_is_required(self, monkeypatch: MonkeyPatch):
        """
        Given a `ChartsView` object
        When `get_permission()` is called
        Then there is a permissions restriction of `IsAuthenticated`
        """
        # Given
        with monkeypatch.context() as m:
            m.setattr(target=config, name="APP_MODE", value="CMS_ADMIN")
            charts_view = ChartsView()

            # When
            permissions_on_view = charts_view.get_permissions()

        # Then
        assert type(permissions_on_view[0]) is permissions.IsAuthenticated
