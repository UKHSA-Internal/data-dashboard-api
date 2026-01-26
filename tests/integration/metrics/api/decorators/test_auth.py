import uuid
from http import HTTPStatus
from unittest import mock

import pytest
from django.urls import path
from rest_framework.test import APIClient
from rest_framework.views import APIView
from django.test import override_settings
from metrics.api.decorators.auth import require_authorisation, RBAC_AUTH_X_HEADER
from django.http import JsonResponse

from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACGroupPermissionFactory,
)
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory

MODULE_PATH = "metrics.api.decorators.auth"


class FakeApiView(APIView):
    @require_authorisation
    def post(self, request, *args, **kwargs):
        try:
            permissions = request.rbac_permissions
        except AttributeError:
            permissions = []
        permissions_data = [p.name for p in permissions]
        return JsonResponse(
            {"message": "Success", "permissions": permissions_data},
            status=HTTPStatus.OK,
        )


urlpatterns = [
    path("api/mock-downloads/", FakeApiView.as_view(), name="mock-downloads"),
]


class TestAuthorisedRoute:
    @property
    def path(self):
        return "/api/mock-downloads/"

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    @mock.patch(f"{MODULE_PATH}.auth.AUTH_ENABLED", False)
    def test_request_succeeds_when_auth_is_disabled(self):
        """
        Given authentication is disabled
        When a request is made to an authorised route
        Then the response is successful
        """
        # Given
        client = APIClient()

        # When
        response = client.post(path=self.path, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "Success", "permissions": []}

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    @mock.patch(f"{MODULE_PATH}.auth.AUTH_ENABLED", True)
    def test_request_succeeds_with_valid_group_id(self):
        """
        Given authentication is enabled
        And a valid `X-GroupId` header is provided
        When a request is made to an authorised route
        Then the response is successful
        """
        # Given
        group_id = uuid.uuid4()
        client = APIClient()
        headers = {f"HTTP_{RBAC_AUTH_X_HEADER}": group_id}
        all_respiratory_data = RBACPermissionFactory.create_record(
            name="all_infectious_respiratory_data",
            theme="infectious_disease",
            sub_theme="respiratory",
        )
        RBACGroupPermissionFactory.create_record(
            name="medical",
            permissions=[all_respiratory_data],
            group_id=group_id,
        )

        # When
        response = client.post(path=self.path, format="json", **headers)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "message": "Success",
            "permissions": [all_respiratory_data.name],
        }

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    @mock.patch(f"{MODULE_PATH}.auth.AUTH_ENABLED", True)
    @pytest.mark.parametrize("group_id", ["invalid", "1", "", None])
    def test_request_with_invalid_group_id(self, group_id):
        """
        Given authentication is enabled
        And an invalid `X-GroupId` header is provided
        When a request is made to an authorised route
        Then the response should contain no permissions
        """
        # Given
        client = APIClient()
        headers = {f"HTTP_{RBAC_AUTH_X_HEADER}": group_id}

        # When
        response = client.post(path=self.path, format="json", **headers)

        # Then
        expected = {"message": "Success", "permissions": []}
        assert response.status_code == HTTPStatus.OK
        assert response.json() == expected

    @pytest.mark.django_db
    @override_settings(ROOT_URLCONF=__name__)
    @mock.patch(f"{MODULE_PATH}.auth.AUTH_ENABLED", True)
    def test_request_succeeds_when_group_id_header_is_missing(self):
        """
        Given authentication is enabled
        And no `X-GroupId` header is provided
        When a request is made to an authorised route
        Then the response should be successful
        And contain no permissions
        """
        # Given
        client = APIClient()
        headers = {}  # No X-GroupId header

        # When
        response = client.post(path=self.path, format="json", **headers)

        # Then
        expected = {"message": "Success", "permissions": []}
        assert response.status_code == HTTPStatus.OK
        assert response.json() == expected
