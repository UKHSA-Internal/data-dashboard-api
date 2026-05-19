import pytest

from cms.auth_content.models.users import User
from tests.factories.auth_content.models.permission_sets import PermissionSetFactory
from tests.factories.auth_content.models.users import UserFactory


class TestUserManager:
    @pytest.mark.django_db
    def test_get_user_with_permission_sets(self):
        """
        Given a number of existing `User` records
        When `get_user_with_permission_sets()` is called
            from the `UserManager`
        Then the user is returned filtered correctly
        """
        user_id = "f907e591-4c49-4847-89b3-665e3c0133a4"

        wildcard_permission = PermissionSetFactory.create_wildcard_permission_set()
        permission_one = PermissionSetFactory.create_permission_set(
            theme=1,
            sub_theme=1,
            topic=2,
            metric=2,
            geography_type=2,
            geography=1,
        )
        permission_two = PermissionSetFactory.create_permission_set(
            theme=1,
            sub_theme=2,
            topic=1,
            metric=2,
            geography_type=1,
            geography=1,
        )

        UserFactory.create_with_permission_sets(
            user_id=user_id,
            permission_sets=[wildcard_permission, permission_one, permission_two],
        )

        # When
        get_user_with_permission_sets = User.objects.get_user_with_permission_sets(
            user_id
        )

        # Then
        assert get_user_with_permission_sets.count() == 1
