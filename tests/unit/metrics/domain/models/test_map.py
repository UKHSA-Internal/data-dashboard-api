from django.http.request import HttpRequest
from rest_framework.request import Request

from metrics.domain.models.map import MapsParameters
from tests.fakes.factories.metrics.rbac_models.rbac_permission import (
    FakeRBACPermissionFactory,
)


class TestMapsParameters:
    def test_rbac_permissions_are_available(self):
        """
        Given an enriched `MapsParameters` model
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
        maps_parameters = MapsParameters(
            date_from="2025-01-01",
            date_to="2025-12-31",
            parameters={
                "theme": rbac_permission.theme.name,
                "sub_theme": rbac_permission.sub_theme.name,
                "topic": rbac_permission.topic.name,
                "metric": "COVID-19_deaths_ONSByWeek",
                "age": "all",
                "sex": "all",
                "stratum": "default",
                "geography_type": "Lower Tier Local Authority",
                "geographies": [],
            },
            accompanying_points=[],
            request=fake_request,
        )

        # Then
        assert maps_parameters.rbac_permissions == [rbac_permission]
