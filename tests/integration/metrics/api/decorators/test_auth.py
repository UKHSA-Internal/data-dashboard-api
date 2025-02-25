import pytest
from http import HTTPStatus
from unittest import mock
from django.urls import path
from rest_framework.test import APIClient
from rest_framework.views import APIView
from django.test import override_settings
from metrics.api.decorators.auth import authorised_route, RBAC_AUTH_X_HEADER
from django.http import JsonResponse

from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACPermissionGroupFactory,
)
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory


MODULE_PATH = "metrics.api.decorators.auth"


class MockDownloadView(APIView):
    @authorised_route
    def post(self, request, *args, **kwargs):
        permissions = getattr(request, "group_permissions", None)
        if permissions:
            permissions_data = [p.name for p in permissions]
        else:
            permissions_data = []
        return JsonResponse(
            {"message": "Success", "permissions": permissions_data},
            status=HTTPStatus.OK,
        )


urlpatterns = [
    path("api/mock-downloads/", MockDownloadView.as_view(), name="mock-downloads"),
]


class TestAuthorisedRoute:
    """
    Tests for the `authorised_route` decorator.
    """

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    def test_request_succeeds_when_auth_is_disabled(self):
        """
        Given authentication is disabled
        When a request is made to an authorised route
        Then the response is successful
        """
        # Given
        client = APIClient()

        with mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", False):
            # When
            response = client.post("/api/mock-downloads/", format="json")

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "Success", "permissions": []}

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    def test_request_succeeds_with_valid_group_id(self):
        """
        Given authentication is enabled
        And a valid `X-GroupId` header is provided
        When a request is made to an authorised route
        Then the response is successful
        """
        # Given
        client = APIClient()
        headers = {f"HTTP_{RBAC_AUTH_X_HEADER}": "medical"}
        all_infectious = RBACPermissionFactory.create_record(
            name="all_infectious_respiratory_data",
            theme_name="infectious_disease",
            sub_theme_name="respiratory",
        )
        _ = RBACPermissionGroupFactory.create_record(
            name="medical",
            permissions=[all_infectious],
        )

        with mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True):
            # When
            response = client.post("/api/mock-downloads/", format="json", **headers)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "message": "Success",
            "permissions": [all_infectious.name],
        }
        # mock_set_rbac.assert_called_once_with(mock.ANY, "medical")

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    def test_request_fails_with_invalid_group_id(self):
        """
        Given authentication is enabled
        And an invalid `X-Group-id` header is provided
        When a request is made to an authorised route
        Then the response contains an error message
        """
        # Given
        client = APIClient()
        headers = {f"HTTP_{RBAC_AUTH_X_HEADER}": "invalid"}

        with mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True):
            # When
            response = client.post("/api/mock-downloads/", format="json", **headers)

        # Then
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "error": "Access Denied",
            "code": 1115,
        }
