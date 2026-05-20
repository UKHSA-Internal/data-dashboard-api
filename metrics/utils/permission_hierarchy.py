"""
Permission hierarchy utilities for deduplicating user permission sets.

This module provides functionality to build a minimal permission hierarchy
from a user's permission sets by removing subsumed (redundant) permissions.
"""

from dataclasses import dataclass
from typing import Any

from django.db.models import QuerySet

from cms.auth_content.models.permission_sets import PermissionSet
from metrics.data.models.core_models.supporting import (
    Geography,
    GeographyType,
    Metric,
    SubTheme,
    Theme,
    Topic,
)


def convert_permission_set_into_hierarchy(raw_permission_sets: dict) -> dict:
    """
    Convert a "permission_set" back into a "permission_set_hierarchy" again
    (the NormalizedPermission class does it the other way round)

    @param {dict} raw_permission_sets, eg:
        {
            "permission_sets": [
                {
                    "theme": {"id": "100", "name": "immunisation"},
                    "sub_theme": {"id": "200", "name": "childhood-vaccines"},
                    "topic": {"id": "215", "name": "MMR1"},
                }
            ],
            "summary": {
                "has_global_access": False
            },
        }

    @return {dict}, eg:
        {
            "permission_set_hierarchy": [
                {
                    "theme": {"id": "100", "name": "immunisation"},
                    "sub_theme": {"id": "200", "name": "childhood-vaccines"},
                    "topic": {"id": "215", "name": "MMR1"},
                }
            ],
            "has_global_access": False,
        }
    """

    permission_set_hierarchy = raw_permission_sets.get("permission_set_hierarchy")
    if permission_set_hierarchy is None:
        permission_set_hierarchy = raw_permission_sets.get("permission_sets", [])

    has_global_access = raw_permission_sets.get("has_global_access")
    if has_global_access is None:
        has_global_access = raw_permission_sets.get("summary", {}).get(
            "has_global_access", False
        )

    return {
        "permission_set_hierarchy": permission_set_hierarchy,
        "has_global_access": bool(has_global_access),
    }


@dataclass
class NormalizedPermission:
    """
    Normalized representation of a permission set for comparison.

    All IDs stored as strings, wildcards as "-1".
    Includes human-readable names for API responses.

    Attributes:
        theme_id: Theme ID or "-1" for wildcard
        sub_theme_id: Sub-theme ID or "-1" for wildcard
        topic_id: Topic ID or "-1" for wildcard
        metric_id: Metric ID or "-1" for wildcard
        geography_type_id: Geography type ID or "-1" for wildcard
        geography_id: Geography code or "-1" for wildcard
        theme_name: Human-readable theme name
        sub_theme_name: Human-readable sub-theme name
        topic_name: Human-readable topic name
        metric_name: Human-readable metric name
        geography_type_name: Human-readable geography type name
        geography_name: Human-readable geography name
    """

    theme_id: str
    sub_theme_id: str
    topic_id: str
    metric_id: str
    geography_type_id: str
    geography_id: str

    # Display names
    theme_name: str = ""
    sub_theme_name: str = ""
    topic_name: str = ""
    metric_name: str = ""
    geography_type_name: str = ""
    geography_name: str = ""

    @classmethod
    def from_permission_set(cls, perm: PermissionSet) -> "NormalizedPermission":
        """
        Create a NormalizedPermission from a PermissionSet instance.

        Args:
            perm: PermissionSet model instance

        Returns:
            NormalizedPermission with populated names
        """
        normalized = cls(
            theme_id=perm.theme or "",
            sub_theme_id=perm.sub_theme or "",
            topic_id=perm.topic or "",
            metric_id=perm.metric or "",
            geography_type_id=perm.geography_type or "",
            geography_id=perm.geography or "",
        )
        normalized._populate_names()
        return normalized

    def _populate_names(self) -> None:
        """Populate human-readable names for all fields."""
        field_mappings = [
            ("theme_id", "theme_name", "theme"),
            ("sub_theme_id", "sub_theme_name", "sub-theme"),
            ("topic_id", "topic_name", "topic"),
            ("metric_id", "metric_name", "metric"),
            ("geography_type_id", "geography_type_name", "geography_type"),
            ("geography_id", "geography_name", "geography"),
        ]

        for id_attr, name_attr, field_name in field_mappings:
            id_value = getattr(self, id_attr)

            if id_value == "-1":
                setattr(self, name_attr, "* (All)")
            elif id_value:
                setattr(self, name_attr, _get_choice_label(field_name, id_value))

    def subsumes(self, other: "NormalizedPermission") -> bool:
        """
        Check if this permission subsumes (is more general than) another.

        A permission subsumes another if it grants access to everything
        the other permission grants. This requires BOTH the theme path
        and geography path to subsume.

        Args:
            other: Another permission to compare against

        Returns:
            True if self subsumes other, False otherwise

        Examples:
            >>> # Wildcard theme subsumes specific theme (same geography)
            >>> p1 = NormalizedPermission(theme_id="-1", ..., geography_id="E12000008")
            >>> p2 = NormalizedPermission(theme_id="2", ..., geography_id="E12000008")
            >>> p1.subsumes(p2)
            True

            >>> # Wildcard geography subsumes specific geography (same theme)
            >>> p3 = NormalizedPermission(theme_id="2", ..., geography_id="-1")
            >>> p4 = NormalizedPermission(theme_id="2", ..., geography_id="E12000008")
            >>> p3.subsumes(p4)
            True

            >>> # Different themes, no subsumption
            >>> p5 = NormalizedPermission(theme_id="2", ..., geography_id="E12000008")
            >>> p6 = NormalizedPermission(theme_id="3", ..., geography_id="E12000008")
            >>> p5.subsumes(p6)
            False
        """
        return self._theme_path_subsumes(other) and self._geography_path_subsumes(other)

    @staticmethod
    def _field_subsumes(self_value: str, other_value: str) -> bool:
        """
        Check if a single field value subsumes another.

        Args:
            self_value: This permission's field value
            other_value: Other permission's field value

        Returns:
            True if self_value subsumes other_value
        """
        # Wildcard subsumes everything
        if self_value == "-1":
            return True

        return self_value == other_value

    def _theme_path_subsumes(self, other: "NormalizedPermission") -> bool:
        """
        Check if this permission's theme path subsumes another's.

        Theme path is: theme → sub_theme → topic → metric

        A wildcard at any level subsumes all specific values at that level
        and all levels below. Empty values are treated as "not specified"
        (less general than wildcard).

        Args:
            other: Another permission to compare against

        Returns:
            True if self's theme path subsumes other's theme path
        """
        # Fixed: Reduced complexity by extracting common logic
        return (
            self._field_subsumes(self.theme_id, other.theme_id)
            and self._field_subsumes(self.sub_theme_id, other.sub_theme_id)
            and self._field_subsumes(self.topic_id, other.topic_id)
            and self._field_subsumes(self.metric_id, other.metric_id)
        )

    def _geography_path_subsumes(self, other: "NormalizedPermission") -> bool:
        """
        Check if this permission's geography path subsumes another's.

        Geography path is: geography_type → geography

        Args:
            other: Another permission to compare against

        Returns:
            True if self's geography path subsumes other's geography path
        """
        return self._field_subsumes(
            self.geography_type_id, other.geography_type_id
        ) and self._field_subsumes(self.geography_id, other.geography_id)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for API serialization.

        Returns compact structure suitable for JWT encoding and API responses.

        Returns:
            Dict with theme, sub_theme, topic, metric, geography_type, geography keys,
            each containing id and name
        """
        return {
            "theme": {
                "id": self.theme_id or None,
                "name": self.theme_name or None,
            },
            "sub_theme": {
                "id": self.sub_theme_id or None,
                "name": self.sub_theme_name or None,
            },
            "topic": {
                "id": self.topic_id or None,
                "name": self.topic_name or None,
            },
            "metric": {
                "id": self.metric_id or None,
                "name": self.metric_name or None,
            },
            "geography_type": {
                "id": self.geography_type_id or None,
                "name": self.geography_type_name or None,
            },
            "geography": {
                "id": self.geography_id or None,
                "name": self.geography_name or None,
            },
        }


def build_permission_hierarchy(permission_sets: QuerySet) -> dict[str, Any]:
    """
    Build deduplicated permission hierarchy from user's permission sets.

    Removes permissions that are subsumed by more general permissions.
    Each permission represents a cross-product of (theme path × geography path).

    This function does NOT query the database for children - it only uses
    the permission set data itself to determine subsumption.

    Args:
        permission_sets: QuerySet of PermissionSet objects for a user

    Returns:
        Dict with 'permission_set_hierarchy' list and 'summary' statistics

    Example:
        >>> # User has:
        >>> # 1. COVID-19 × All geographies (wildcard)
        >>> # 2. COVID-19 × South East region (SUBSUMED by #1)
        >>> perms = PermissionSet.objects.filter(user__user_id=some_uuid)
        >>> hierarchy = build_permission_hierarchy(perms)
        >>> len(hierarchy['permission_set_hierarchy'])
        1  # Only #1 remains
        >>> hierarchy['summary']['removed_count']
        1
    """
    # Convert all permission sets to normalized form
    normalized_perms = [
        NormalizedPermission.from_permission_set(perm) for perm in permission_sets
    ]

    deduplicated = _remove_subsumed_permissions(normalized_perms)

    summary = _build_summary(normalized_perms, deduplicated)

    return {
        "permission_sets": [perm.to_dict() for perm in deduplicated],
        "summary": summary,
    }


def _remove_subsumed_permissions(
    permissions: list[NormalizedPermission],
) -> list[NormalizedPermission]:
    """
    Remove permissions that are subsumed by more general permissions.

    Algorithm:
    1. Iterate through each permission
    2. Check if it's subsumed by any permission already in the result
    3. If not subsumed, remove any existing permissions that this one subsumes
    4. Add this permission to the result

    Args:
        permissions: List of normalized permissions

    Returns:
        List with subsumed permissions removed

    Example:
        >>> perms = [
        ...     NormalizedPermission(theme_id="2", ..., geography_id="-1"),  # General
        ...     NormalizedPermission(theme_id="2", ..., geography_id="E12000008"),  # Specific
        ... ]
        >>> result = _remove_subsumed_permissions(perms)
        >>> len(result)
        1  # Only the general permission remains
    """
    result = []

    for perm in permissions:
        # Check if this permission is subsumed by any already in result
        is_subsumed = any(existing.subsumes(perm) for existing in result)

        if is_subsumed:
            # Skip this permission - it's redundant
            continue

        # This permission is not subsumed, so check if it subsumes any existing ones
        # Remove any existing permissions that this one subsumes
        result = [existing for existing in result if not perm.subsumes(existing)]

        result.append(perm)

    return result


def get_deduplicated_permissions(
    permission_sets: QuerySet,
) -> list[NormalizedPermission]:
    """
    Get deduplicated permissions without hierarchy structure.

    Useful for passing to grouping functions.

    Args:
        permission_sets: QuerySet of PermissionSet objects

    Returns:
        List of deduplicated NormalizedPermission objects
    """
    normalized_perms = [
        NormalizedPermission.from_permission_set(perm) for perm in permission_sets
    ]
    return _remove_subsumed_permissions(normalized_perms)


def _build_summary(
    original: list[NormalizedPermission],
    deduplicated: list[NormalizedPermission],
) -> dict[str, Any]:
    """
    Build summary statistics about the permission hierarchy.

    Args:
        original: Original list of permissions before deduplication
        deduplicated: List after removing subsumed permissions

    Returns:
        Dict with statistics about the deduplication process
    """
    # Check for global wildcard (theme + geography both wildcarded)
    has_global_access = any(
        perm.theme_id == "-1" and perm.geography_type_id == "-1"
        for perm in deduplicated
    )

    wildcard_themes = [
        perm.theme_name for perm in deduplicated if perm.theme_id == "-1"
    ]

    return {
        "total_permission_sets": len(original),
        "deduplicated_count": len(deduplicated),
        "removed_count": len(original) - len(deduplicated),
        "has_global_access": has_global_access,
        "wildcard_themes": wildcard_themes,
    }


@staticmethod
def _get_choice_label(field_name: str, value: str) -> str:
    """Get the display label for a choice field"""

    # Map field names to their model managers
    field_manager_map = {
        "theme": Theme.objects,
        "sub-theme": SubTheme.objects,
        "topic": Topic.objects,
        "metric": Metric.objects,
        "geography": Geography.objects,
        "geography_type": GeographyType.objects,
    }

    manager = field_manager_map.get(field_name)

    if manager:
        name = (
            manager.get_name_by_code(value)
            if field_name == "geography"
            else manager.get_name_by_id(int(value))
        )
        return name or value

    return value
