from http import HTTPStatus
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from tests.factories.auth_content.models.permission_sets import PermissionSetFactory
from tests.factories.auth_content.models.users import UserFactory


class TestPermissionSetByUser:
    @property
    def path(self) -> str:
        return "/api/public/user"
    

    @pytest.mark.django_db
    def test_returns_400_for_invalid_uuid(self):
        """
        Given an invalid UUID format
        When requesting hierarchy
        Then a 400 is returned with validation error
        """
        # Given
        client = APIClient()
        invalid_uuid = "not-a-valid-uuid"

        # When
        path = f"{self.path}/{invalid_uuid}/permissions/hierarchy"
        response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "user_id" in response.data

    @pytest.mark.django_db
    def test_returns_empty_permission_set_hierarchy_for_invalid_uuid(self):
        """
        Given an invalid UUID format
        When requesting hierarchy
        Then a 400 is returned with validation error
        """
        # Given
        client = APIClient()
        user_id = str(uuid4())

        # When
        path = f"{self.path}/{user_id}/permissions/hierarchy"
        response = client.get(path=path)

        # Then
        assert response.data["permission_sets"] == []

    @pytest.mark.django_db
    def test_global_wildcard_subsumes_everything(self):
        """
        Given a user with a global wildcard and specific permissions
        When requesting their hierarchy
        Then only the global wildcard remains
        """
        # Given
        client = APIClient()
        user_id = str(uuid4())

        # Global wildcard: All themes × All geographies
        global_perm = PermissionSetFactory.create_wildcard_permission_set()

        # Specific permission (should be subsumed)
        specific_perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        UserFactory.create_with_permission_sets(
            user_id=user_id, permission_sets=[global_perm, specific_perm]
        )

        # When
        path = f"{self.path}/{user_id}/permissions/hierarchy"
        response = client.get(path=path)

        # Then
        result = response.data

        summary = result["permission_sets"]["summary"]
        print(summary)

        assert summary["total_permission_sets"] == 2
        assert summary["deduplicated_count"] == 1
        assert summary["has_global_access"] is True

        hierarchy = result["permission_sets"]["permission_sets"]
        assert len(hierarchy) == 1
        assert hierarchy[0]["theme"]["id"] == "-1"
        assert hierarchy[0]["geography_type"]["id"] == "-1"
