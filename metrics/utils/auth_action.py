from typing import Any

from metrics.api.models import (
    ApiPermission,
)


def is_wildcard(group_permission: ApiPermission, attr: str) -> bool:
    return not getattr(group_permission, attr)


def new_match_dict() -> dict[str, bool]:
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


class MatchThemeSubthemeAction:

    def execute(self, data: Any, group_permission: ApiPermission) -> bool:
        perm_theme_subtheme = [
            group_permission.theme.name,
            group_permission.sub_theme.name,
        ]
        data_theme_subtheme = [data["theme"], data["sub_theme"]]
        return perm_theme_subtheme == data_theme_subtheme


class MatchTopLevelFieldsAction:

    def __init__(self, field_name: str):
        self.field_name = field_name

    def execute(self, data: Any, group_permission: ApiPermission) -> bool:
        group_permission_field = getattr(group_permission, self.field_name)
        permission_theme_value = getattr(group_permission_field, "name")
        if data[self.field_name] == permission_theme_value:
            return True
        return False


class MatchFieldAction:

    def __init__(self, field_name: str):
        self.field_name = field_name

    def execute(self, data: Any, group_permission: ApiPermission) -> bool:
        permission_stratum = getattr(group_permission, self.field_name, None)
        permission_value = getattr(permission_stratum, "name", None)
        if (
            is_wildcard(group_permission, self.field_name)
            or data[self.field_name] == permission_value
        ):
            return True
        return False


class ValidationAction:

    def __init__(self):
        self.did_match = False

    def execute(self, matched_plots) -> None:
        matched = []
        for match_plot in matched_plots:
            matched.append(all(values for values in match_plot.values()))
        self.did_match = any(matched)
