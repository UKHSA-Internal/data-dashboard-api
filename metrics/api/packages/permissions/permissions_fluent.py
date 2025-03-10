from typing import Any

from metrics.api.packages.permissions import (
    BaseAction,
    MatchFieldAction,
    MatchThemeSubThemeFieldsAction,
    new_match_dict,
)
from metrics.data.models.rbac_models import RBACPermission


class FluentPermissionsError(Exception):
    """
    Raised when permission validation fails in FluentPermissions.

    This exception is triggered when `validate()` is called but no valid permission match exists.
    """


class FluentPermissions:
    """
    A class for handling Role-Based Access Control (RBAC) permissions using a fluent API.

    This class checks multiple fields against a list of RBAC permissions (`group_permissions`),
    storing the results in a list of dictionaries where:

    - **Keys** represent the field names being checked (e.g., "theme", "sub_theme", "topic").
    - **Values** are boolean flags (`True/False`), indicating whether each field matched
        the corresponding permission.

    ### Setup:
    1. Instantiate `FluentPermissions` with `data` and `group_permissions`.
    2. Use `.add_field(field_name)` to define which fields should be checked.
    3. Call `.execute()` to evaluate permissions.
    4. Use `.match_fields_all` to access the results.
    5. Call `.validate()` to ensure at least one valid match exists.

    ### Example Usage:
    from metrics.data.models.rbac_models import RBACPermission
    from metrics.api.decorators.permissions_fluent import FluentPermissions, FluentPermissionsError

    # Define user permissions (mocked for example)
    user_permission = RBACPermission()
    user_permission.theme.name = "infectious_disease"
    user_permission.sub_theme.name = "respiratory"
    user_permission.topic.name = "COVID-19"

    # Data to check
    data = {
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
    }

    # Create FluentPermissions instance
    permissions = FluentPermissions(
        data=data,
        group_permissions=[user_permission],
    )

    # Add fields and execute permission check
    permissions.add_field("theme").add_field("sub_theme").add_field("topic").execute()

    # Validate access
    try:
        permissions.validate()
        print("Access granted")
    except FluentPermissionsError:
        print("Access denied")
    """

    # Stores the matching status for individual fields in the current execution cycle.
    # It is a dictionary where the keys are field names (e.g., "theme", "metric"),
    # and the values are boolean flags indicating whether the field matched a permission.
    match_fields: dict[str, bool]

    # A list of match dictionaries from multiple permission evaluations.
    # Each dictionary represents the result of a single permission check.
    # This is a read-only property accessed via the `match_fields_all` getter.
    _match_fields_all: list[dict[str, bool]]

    # A list of field names that will be checked in the permission validation process.
    # The fields are added dynamically using the `add_field()` method.
    field_names: list[str]

    # Represents a single RBACPermission object being evaluated.
    # Used during individual permission checks in the execution process.
    group_permission: RBACPermission

    # A list of RBACPermission objects representing all the permissions
    # available for the user or role being evaluated.
    group_permissions: list[RBACPermission]

    def __init__(self, *, data: Any, group_permissions: list[RBACPermission]):
        self.data = data
        self.group_permissions = group_permissions
        self.field_names = []
        self._match_fields_all = []

    @property
    def match_fields_all(self) -> list[dict[str, bool]]:
        """Read-only property for accessing the match results."""
        return self._match_fields_all

    def add_field(self, field_name: str) -> "FluentPermissions":
        """
        Adds a field to be checked during permission validation.

        Fields added with this method will be evaluated when `execute()` is called.

        Args:
            field_name (str): The name of the field to check.

        Returns:
            FluentPermissions: The current instance, allowing method chaining.
        """
        self.field_names.append(field_name)
        return self

    def execute(self) -> "FluentPermissions":
        """
        Given a set of user permissions (`group_permissions`)
        When `execute()` is called
        Then it evaluates field matches and stores results in `_match_fields_all`

        This method iterates through each `RBACPermission` in `group_permissions`,
        comparing its fields against the provided `data`. If the `theme` and `sub_theme`
        do not match, the permission check is skipped for optimization.

        Returns:
            FluentPermissions: Returns the instance itself for method chaining.

        Example:
            ```python
            permissions = FluentPermissions(data=data, group_permissions=[user_permission])
            permissions.add_field("theme").add_field("sub_theme").execute()
            matches = permissions.match_fields_all  # Access stored results
            ```
        """
        for group_permission in self.group_permissions:
            self.match_fields = new_match_dict()
            # Optimization - continue if theme or sub_theme don't match
            if not self._match_theme_sub_theme(group_permission):
                continue

            theme_sub_theme_action = MatchThemeSubThemeFieldsAction(data=self.data)
            field_action = MatchFieldAction(data=self.data)

            self._execute_actions_and_store_results(
                theme_sub_theme_action=theme_sub_theme_action,
                field_action=field_action,
                group_permission=group_permission,
            )
            self._match_fields_all.append(self.match_fields)
        return self

    def validate(self) -> None:
        """
        Ensures at least one set of permissions fully matches the provided data.

        This method checks whether any match in `_match_fields_all` contains all `True` values.
        If no complete match is found, it raises a `FluentPermissionsError`.

        Raises:
            FluentPermissionsError: If no valid permission match exists.
        """
        if not self._validate_match_field():
            raise FluentPermissionsError

    def _execute_actions_and_store_results(
        self,
        *,
        theme_sub_theme_action: BaseAction,
        field_action: BaseAction,
        group_permission: RBACPermission,
    ) -> None:
        """Execute actions & store results in match_fields dict"""
        for field_name in self.field_names:
            match field_name:
                case "theme" | "sub_theme":
                    self._run_action(
                        theme_sub_theme_action, field_name, group_permission
                    )
                case _:
                    self._run_action(field_action, field_name, group_permission)

    def _match_theme_sub_theme(self, group_permission: RBACPermission) -> bool:
        """
        Checks if the given group permission matches the `theme` and `sub_theme` in `self.data`.
        Returns False if `theme` or `sub_theme` keys are missing.
        """
        theme = self.data.get("theme")
        sub_theme = self.data.get("sub_theme")

        if theme is None or sub_theme is None:
            return False
        return [
            group_permission.theme.name,
            group_permission.sub_theme.name,
        ] == [self.data["theme"], self.data["sub_theme"]]

    def _validate_match_field(self) -> bool:
        matched = [
            all(values for values in match_plot.values())
            for match_plot in self._match_fields_all
        ]
        return any(matched)

    def _run_action(
        self, action: BaseAction, field_name: str, group_permission: RBACPermission
    ):
        self.match_fields = action.execute(
            field_name=field_name,
            group_permission=group_permission,
            match_fields=self.match_fields,
        )
