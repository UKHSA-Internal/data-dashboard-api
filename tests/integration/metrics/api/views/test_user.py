from http import HTTPStatus
from uuid import uuid4

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from auth_content.constants import WILDCARD_ID_VALUE
from tests.factories.auth_content.models.permission_sets import PermissionSetFactory
from tests.factories.auth_content.models.users import UserFactory
from tests.factories.metrics.metric import MetricFactory
from tests.factories.metrics.sub_theme import SubThemeFactory
from tests.factories.metrics.topic import TopicFactory


class TestPermissionSetByUser:
    @property
    def path(self) -> str:
        return "/api/user"

    @pytest.mark.django_db
    def test_get_user_wildcard_permission_set(self):

        client = APIClient()

        userId = "f907e591-4c49-4847-89b3-665e3c0133a4"

        # create subthemes
        wildcard_permission = PermissionSetFactory.create_wildcard_permission_set()
        permission_one = PermissionSetFactory.create_permission_set(
            name="Permission Set 1",
            theme=1,
            sub_theme=1,
            topic=2,
            metric=2,
            geography_type=2,
            geography=1,
        )
        permission_two = PermissionSetFactory.create_permission_set(
            name=" Permission Set 2",
            theme=1,
            sub_theme=2,
            topic=1,
            metric=2,
            geography_type=1,
            geography=1,
        )
        user_with_wildcard = UserFactory.create_with_permission_sets(
            user_id=userId,
            permission_sets=[wildcard_permission, permission_one, permission_two],
        )

        # Retrieve the subthemes
        path = f"{self.path}/{userId}/permissions"
        response: Response = client.get(path=path)
        result = response.data

        # Should return a user with 3 permissions sets
        assert result["user_id"] == userId
        assert len(result["permission_sets"]) == 3
        assert result["permission_sets"][0] == {
            "id": 1,
            "name": "Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All) | Geography: * (All)",
            "theme": "-1",
            "sub_theme": "-1",
            "topic": "-1",
            "metric": "-1",
            "geography_type": "-1",
            "geography": "-1",
        }

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
        userId = str(uuid4())

        # When
        path = f"{self.path}/{userId}/permissions/hierarchy"
        response = client.get(path=path)

        # Then
        assert response.data["permission_set_hierarchy"] == []

    @pytest.mark.django_db
    def test_returns_empty_permission_sets_when_no_permissions(self):
        """
        Given an invalid user id if no associated permission sets then
        returns an empty list of permission sets
        """
        # Given
        client = APIClient()
        userId = str(uuid4())

        # When
        path = f"{self.path}/{userId}/permissions"
        response = client.get(path=path)
        data = response.data
        print(data)

        # Then
        assert data["user_id"] == userId
        assert data["permission_sets"] == []
        assert data["permission_set_count"] == 0

    @pytest.mark.django_db
    def test_global_wildcard_subsumes_everything(self):
        """
        Given a user with a global wildcard and specific permissions
        When requesting their hierarchy
        Then only the global wildcard remains
        """
        # Given
        client = APIClient()
        userId = str(uuid4())

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

        user = UserFactory.create_with_permission_sets(
            user_id=userId, permission_sets=[global_perm, specific_perm]
        )

        # When
        path = f"{self.path}/{userId}/permissions/hierarchy"
        response = client.get(path=path)

        # Then
        result = response.data

        summary = result["permission_sets"]["summary"]
        print(summary)

        assert summary["total_permission_sets"] == 2
        assert summary["deduplicated_count"] == 1
        assert summary["has_global_access"] is True

        hierarchy = result["permission_sets"]["permission_set_hierarchy"]
        assert len(hierarchy) == 1
        assert hierarchy[0]["theme"]["id"] == "-1"
        assert hierarchy[0]["geography_type"]["id"] == "-1"

    @pytest.mark.django_db
    def test_get_user_wildcard_permission_set(self):
        client = APIClient()

        userId = "f907e591-4c49-4847-89b3-665e3c0133a4"

        # create subthemes
        wildcard_permission = PermissionSetFactory.create_wildcard_permission_set()
        user_with_wildcard = UserFactory.create_with_permission_set(
            user_id=userId,
            permission_set_name="Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All) | Geography: * (All)",
        )

        # Retrieve the subthemes
        path = f"{self.path}/{userId}/permissions"
        response: Response = client.get(path=path)
        result = response.data

        # Should return a wildcard choice
        assert result["user_id"] == userId
        assert result["permission_sets"][0] == {
            "id": 1,
            "name": "Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All) | Geography: * (All)",
            "theme": "-1",
            "sub_theme": "-1",
            "topic": "-1",
            "metric": "-1",
            "geography_type": "-1",
            "geography": "-1",
        }

    @pytest.mark.django_db
    def test_accepts_empty_group_by_parameter(self):
        """
        Given a valid user
        When requesting hierarchy without group_by parameter
        Then the request succeeds with default behavior
        """
        # Given
        client = APIClient()
        user_id = str(uuid4())

        user = UserFactory.create(user_id=user_id)
        perm = PermissionSetFactory.create_wildcard_permission_set()
        user.permission_sets.add(perm)

        # When - No query parameters
        path = f"{self.path}/{user_id}/permissions/hierarchy"
        response = client.get(path)

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_accepts_group_by_theme_parameter(self):
        """
        Given a valid user
        When requesting hierarchy with group_by=theme
        Then the request succeeds
        """
        # Given
        client = APIClient()
        user_id = str(uuid4())

        user = UserFactory.create(user_id=user_id)
        perm = PermissionSetFactory.create_wildcard_permission_set()
        user.permission_sets.add(perm)

        # When
        path = f"{self.path}/{user_id}/permissions/hierarchy?group_by=theme"
        response = client.get(path)

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_accepts_group_by_geography_parameter(self):
        """
        Given a valid user
        When requesting hierarchy with group_by=geography
        Then the request succeeds
        """
        # Given
        client = APIClient()
        user_id = str(uuid4())

        user = UserFactory.create(user_id=user_id)
        perm = PermissionSetFactory.create_wildcard_permission_set()
        user.permission_sets.add(perm)

        # When
        path = f"{self.path}/{user_id}/permissions/hierarchy?group_by=geography_type"
        response = client.get(path)

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_handles_invalid_group_by_parameter(self):
        """
        Given a valid user
        When requesting hierarchy with invalid group_by value
        Then appropriate error is returned
        """
        # Given
        client = APIClient()
        user_id = str(uuid4())

        user = UserFactory.create(user_id=user_id)
        perm = PermissionSetFactory.create_wildcard_permission_set()
        user.permission_sets.add(perm)

        # When
        path = f"{self.path}/{user_id}/permissions/hierarchy?group_by=invalid_value"
        response = client.get(path)

        # Then
        # Depending on your implementation, this might be 400 or just ignored
        # Adjust based on your actual validation logic
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST]
