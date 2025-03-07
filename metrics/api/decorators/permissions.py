import logging
from functools import wraps

from metrics.api.packages.permissions import (
    FluentPermissions,
    FluentPermissionsError,
)
from metrics.api.settings.private_api import is_auth_enabled
from metrics.data.models.rbac_models import (
    RBACPermission,
)

logger = logging.getLogger(__name__)


def filter_by_permissions():
    def decorator(serializer_class):
        _init = serializer_class.__init__

        @wraps(_init)
        def init(self, *args, **kwargs):
            super(serializer_class, self).__init__(*args, **kwargs)
            original_to_representation = self.to_representation

            if not is_auth_enabled():
                new_to_representation = _new_representation_public(
                    self=self,
                    representation=original_to_representation,
                )
            else:
                new_to_representation = _new_to_representation_private(
                    self=self,
                    representation=original_to_representation,
                )

            self.to_representation = new_to_representation

        serializer_class.__init__ = init
        return serializer_class

    return decorator


def _new_representation_public(*, self, representation):
    def wrapper(instance):
        data = representation(instance)
        data.pop("is_public")
        return data

    return wrapper


def _new_to_representation_private(*, self, representation):
    def wrapper(instance):
        data = representation(instance)

        # Handle public data
        if data["is_public"]:
            data.pop("is_public")
            return data
        data.pop("is_public")

        # Get RBAC permissions from request object
        request = self.context.get("request", None)
        group_permissions: list[RBACPermission] = getattr(
            request, "group_permissions", []
        )

        # If there are no permissions but the data is not public return None
        if not group_permissions:
            return None

        try:
            fluent_permissions = FluentPermissions(
                group_permissions=group_permissions,
                data=data,
            )
            (
                fluent_permissions.add_field("theme")
                .add_field("sub_theme")
                .add_field("topic")
                .add_field("geography_type")
                .add_field("geography")
                .add_field("metric")
                .add_field("age")
                .add_field("stratum")
                .execute()
                .validate()
            )
        except FluentPermissionsError:
            return None
        return data

    return wrapper
