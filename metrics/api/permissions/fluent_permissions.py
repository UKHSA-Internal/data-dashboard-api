from collections.abc import Iterable
from dataclasses import dataclass

from metrics.data.models.rbac_models import RBACPermission


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
            "age",
            "stratum",
        ]

        for field in fields:
            supporting_model = getattr(rbac_permission, field)
            requested_value: str = getattr(self.requested_data_parameters, field)
            if (
                supporting_model is not None
                and requested_value != supporting_model.name
            ):
                return False

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
        for rbac_permission in rbac_permissions:
            if self.check_permission_allows_access(rbac_permission=rbac_permission):
                return True
        return False
