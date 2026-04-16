from http import HTTPStatus

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
        user_with_wildcard = UserFactory.create_with_permission_set(
            user_id=userId, permission_set_name="Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All) | Geography: * (All)")

        # Retrieve the subthemes
        path = f"{self.path}/{userId}/permissions"
        response: Response = client.get(path=path)
        result = response.data

        # Should return a wildcard choice
        print(result)
        assert result["user_id"] == userId
        assert result["permission_sets"][0] == {
            "id": 1,
            "name": "Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All) | Geography: * (All)",
            "theme": "-1",
            "sub_theme": "-1",
            "topic": "-1",
            "metric": "-1",
            "geography_type": "-1",
            "geography": "-1"
        }

    @pytest.mark.django_db
    def test_get_user_wildcard_permission_set(self):

        client = APIClient()

        userId = "f907e591-4c49-4847-89b3-665e3c0133a4"

        # create subthemes
        wildcard_permission = PermissionSetFactory.create_wildcard_permission_set()
        permission_one = PermissionSetFactory.create_permission_set(
            name="Permission Set 1", theme=1, sub_theme=1, topic=2, metric=2, geography_type=2, geography=1)
        permission_two = PermissionSetFactory.create_permission_set(
            name=" Permission Set 2", theme=1, sub_theme=2, topic=1, metric=2, geography_type=1, geography=1)
        user_with_wildcard = UserFactory.create_with_permission_sets(
            user_id=userId, permission_sets=[wildcard_permission, permission_one, permission_two])

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
            "geography": "-1"
        }
