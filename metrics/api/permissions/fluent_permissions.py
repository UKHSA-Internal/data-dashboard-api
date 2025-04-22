from collections.abc import Iterable
from dataclasses import dataclass

from metrics.api.settings.auth import AUTH_ENABLED
from metrics.data.models.rbac_models import RBACPermission


def validate_permissions(
    *,
    theme: str,
    sub_theme: str,
    topic: str,
    metric: str,
    geography: str,
    geography_type: str,
    rbac_permissions: Iterable[RBACPermission]
) -> bool:

    if not AUTH_ENABLED:
        return False

    requested_data_parameters = RequestedDataParameters(
        theme=theme,
        sub_theme=sub_theme,
        topic=topic,
        metric=metric,
        geography=geography,
        geography_type=geography_type,
        age="",
        sex="",
        stratum="",
    )

    fluent_permissions = FluentPermissions(
        requested_data_parameters=requested_data_parameters
    )

    return fluent_permissions.check_if_any_permissions_allow_access(
        rbac_permissions=rbac_permissions
    )


@dataclass
class RequestedDataParameters:
    theme: str
    sub_theme: str
    topic: str
    metric: str
    geography: str
    geography_type: str
    age: str
    sex: str
    stratum: str


class FluentPermissions:
    def __init__(self, *, requested_data_parameters: RequestedDataParameters):
        self.requested_data_parameters = requested_data_parameters

    def check_permission_allows_access(self, rbac_permission: RBACPermission) -> bool:
        """Checks if the given `rbac_permission` provides access `requested_data_parameters`

        Notes:
            This provides wildcard matching in accordance with the hierarchy.
            For example, if the `theme` is matched and the rest of the permission is empty
            this is considered a wildcard, and will match data parameters.

        Args:
             `rbac_permission`: The `RBACPermission` model which contains
                the individual permission details

        Returns:
            True if the given permission allows access to the requested dataset.
            False otherwise.

        """
        fields = [
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography_type",
            "geography",
        ]

        for field in fields:
            allowed_model = getattr(rbac_permission, field, None)
            # Django throws a `RelatedObjectDoesNotExist` error when the related attr is `None`.
            # In this case we're happy to just bury the error and handle the returned object as `None`
            if not allowed_model:
                # Since the field was not specified on the `RBACPermission`.
                # We consider this to be a wildcard and skip to the next field for evaluation.
                continue

            requested_value: str = getattr(self.requested_data_parameters, field)
            if requested_value != allowed_model.name:
                # The field was specified on the `RBACPermission`.
                # And it has not matched, so we mark the permission as False
                # i.e. this permission does not allow access to the dataset
                return False

        # All the fields have been evaluated as either:
        # - The field was `None` and therefore wildcarded
        # - The field was a match
        # In this case we can say the permission does allow access to the dataset
        return True

    def check_if_any_permissions_allow_access(
        self, rbac_permissions: Iterable[RBACPermission]
    ) -> bool:
        """Checks if any of the given `rbac_permissions` provides access to the `requested_data_parameters`

        Args:
             `rbac_permissions`: The `RBACPermission` models which contain
                the details for each permission.

        Returns:
            True if any of the given permissions allows access to the requested dataset.
            False otherwise.

        """
        return any(
            self.check_permission_allows_access(rbac_permission=rbac_permission)
            for rbac_permission in rbac_permissions
        )
