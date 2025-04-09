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
            rbac_permission_value: str = getattr(rbac_permission, field)
            requested_value: str = getattr(self.requested_data_parameters, field)
            if (
                rbac_permission_value is not None
                and requested_value != rbac_permission_value.name
            ):
                return False

        return True

    def check_rbac_permissions(self, rbac_permissions: list[RBACPermission]) -> bool:
        for rbac_permission in rbac_permissions:
            is_access_allowed: bool = self.check_permission_allows_access(
                rbac_permission=rbac_permission
            )
            if is_access_allowed:
                return True

        return False
