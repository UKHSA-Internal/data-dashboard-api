from typing import List

import factory
from metrics.data.models.rbac_models import (
    RBACPermission,
    RBACGroupPermission,
)


class RBACPermissionGroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = RBACGroupPermission

    @classmethod
    def create_record(
        cls,
        name: str = "default",
        permissions: List[RBACPermission] = [],
        **kwargs,
    ):

        group = cls.create(name=name, **kwargs)
        # Fetch or create permissions and add them to the group
        for permission in permissions:
            group.permissions.add(permission)
        return group
