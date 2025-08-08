from django.http.request import HttpRequest
from rest_framework.request import Request

from metrics.domain.models.charts.subplot_charts import Subplots
from tests.fakes.factories.metrics.rbac_models.rbac_permission import (
    FakeRBACPermissionFactory,
)


class TestSubplotChartSubplots:
    def test_rbac_permissions_are_available(self):
        """
        Given an enriched `SubplotChartSubplots` model
        When the `rbac_permissions` property is accessed
        Then the `RBACPermission` which are on the request
            will be returned
        """
        # Given
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
        )
        fake_request = Request(request=HttpRequest())
        fake_request.rbac_permissions = [rbac_permission]

        # When
        subplot_parameters = Subplots(
            subplot_title="Subplot Title",
            x_axis="X-Axis",
            y_axis="Y-Axis",
            plots=[],
            request=fake_request,
        )

        # Then
        assert subplot_parameters.rbac_permissions == [rbac_permission]
