from abc import ABC, abstractmethod

from metrics.data.models.rbac_models import RBACPermission


def _is_wildcard(group_permission: RBACPermission, attr: str) -> bool:
    return not getattr(group_permission, attr)


def new_match_dict() -> dict[str, bool]:
    """
    Creates a new match dictionary with default values set to False.

    This dictionary is used to track whether each field has a valid match
    during permission evaluation.

    Returns:
        dict[str, bool]: A dictionary with predefined keys representing
        permission fields, all initialized to False.

    Example:
        ```python
        match_fields = new_match_dict()
        print(match_fields)
        # Output: {'theme': False, 'sub_theme': False, 'topic': False, ...}
        ```
    """
    return {
        "theme": False,
        "sub_theme": False,
        "topic": False,
        "geography_type": False,
        "geography": False,
        "metric": False,
        "age": False,
        "stratum": False,
    }


class BaseAction(ABC):
    """
    Abstract base class for permission matching actions.

    This class defines the interface for actions that evaluate whether a field
    in `data` matches the corresponding field in `group_permission`.
    Subclasses must implement the `execute()` method.

    Attributes:
        data (Dict[str,str]): The input data against which permissions will be checked.
    """

    def __init__(self, *, data: dict[str, str]):
        self.data = data

    @abstractmethod
    def execute(
        self,
        *,
        field_name: str,
        group_permission: RBACPermission,
        match_fields: dict[str, bool]
    ) -> dict[str, bool]:
        """
        Executes the permission check for a specific field.

        Args:
          field_name (str): The name of the field to validate.
          group_permission (RBACPermission): The permission object containing allowed values.
          match_fields (dict[str, bool]): A dictionary tracking which fields matched.

        Returns:
          dict[str, bool]: Updated `match_fields` dictionary with the result of the check.
        """


class MatchThemeSubThemeFieldsAction(BaseAction):
    """
    Action for matching theme and subtheme fields in RBAC permissions.

    This action checks whether the provided `field_name` in `data` matches the corresponding
    value in `group_permission`. If a match is found, the field is marked as `True` in
    `match_fields`.
    """

    def execute(
        self,
        *,
        field_name: str,
        group_permission: RBACPermission,
        match_fields: dict[str, bool]
    ) -> dict[str, bool]:
        group_permission_field = getattr(group_permission, field_name)
        permission_theme_value = group_permission_field.name
        if self.data[field_name] == permission_theme_value:
            match_fields[field_name] = True
        return match_fields


class MatchFieldAction(BaseAction):
    """
    Action for matching general fields in RBAC permissions.

    This action checks whether the specified `field_name` in `data` matches the corresponding
    value in `group_permission`. If a match is found or if the permission allows a wildcard,
    the field is marked as `True` in `match_fields`.

    Inherits from:
        BaseAction: Defines the structure for permission-matching actions.
    """

    def execute(
        self,
        *,
        field_name: str,
        group_permission: RBACPermission,
        match_fields: dict[str, bool]
    ) -> dict[str, bool]:
        permission_stratum = getattr(group_permission, field_name, None)
        permission_value = getattr(permission_stratum, "name", None)
        if (
            _is_wildcard(group_permission, field_name)
            or self.data[field_name] == permission_value
        ):
            match_fields[field_name] = True
        return match_fields
