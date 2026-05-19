"""
Non-public permission validation, filtering and matching functions
"""

import logging
from typing import Literal, NotRequired, TypedDict

from metrics.data.models.core_models.supporting import (
    Geography,
    GeographyType,
    Metric,
    Topic,
)

logger = logging.getLogger(__name__)

# Our permission resources, e.g. anything that you can filter by permission
PermissionFilterResource = Literal[
    "theme",
    "sub_theme",
    "topic",
    "metric",
    "geography_type",
    "geography",
]


class PermissionSetLevel(TypedDict):
    """
    The "id" is the actual permission.
    The "name" is just some blurb describing it.
    """

    id: str  # can be "-1", therefore a string
    name: str


class PermissionHierarchy(TypedDict):
    """
    Our permission resources, e.g. anything that you can filter by permission.
    Each one of them is optional, but at least one of them has to be provided.
    """

    theme: NotRequired[PermissionSetLevel]
    sub_theme: NotRequired[PermissionSetLevel]
    topic: NotRequired[PermissionSetLevel]
    metric: NotRequired[PermissionSetLevel]
    geography_type: NotRequired[PermissionSetLevel]
    geography: NotRequired[PermissionSetLevel]


def check_if_any_permissions_allow_access(
    *,
    jwt_permissions: dict | None,
    theme: str = "",
    sub_theme: str = "",
    topic: str,
    metric: str,
    geography_type: str,
    geography: str,
) -> bool:
    """
    This is our CORE PERMISSION-CHECKING function.

    Resolve request names to IDs and return whether any
    of the passed API filters are being satisfied through
    the user's permissions defined in the jwt_permissions.

    Any of our 6 passed permission fields is optional. If
    none of them is set, no permission is given.

    @param {dict | None} jwt_permissions, eg:
            {
                "permission_set_hierarchy": [
                    {
                        "theme": {"id": "100", "name": "immunisation"},
                        "sub_theme": {"id": "133", "name": "childhood-vaccines"},
                        "topic": {"id": "-1", "name": "* (All)"},
                    }
                ]
            }

    @return {bool}
    """

    topic_record = None
    if topic:
        if theme and sub_theme:
            topic_record = Topic.objects.filter(
                name=topic,
                sub_theme__name=sub_theme,
                sub_theme__theme__name=theme,
            ).first()
        if topic_record is None:
            topic_record = Topic.objects.filter(name=topic).first()

    metric_record = None
    if metric:
        metric_record = Metric.objects.filter(name=metric).first()

    geography_type_record = None
    if geography_type:
        geography_type_record = GeographyType.objects.filter(
            name=geography_type
        ).first()

    geography_record = None
    if geography:
        geography_queryset = Geography.objects.filter(name=geography)
        if geography_type_record:
            geography_queryset = geography_queryset.filter(
                geography_type_id=geography_type_record.id
            )
        geography_record = geography_queryset.first()

    requested_filters: dict[PermissionFilterResource, str | None] = {
        "theme": str(topic_record.sub_theme.theme_id) if topic_record else None,
        "sub_theme": str(topic_record.sub_theme_id) if topic_record else None,
        "topic": str(topic_record.id) if topic_record else None,
        "metric": str(metric_record.id) if metric_record else None,
        "geography_type": (
            str(geography_type_record.id) if geography_type_record else None
        ),
        "geography": (
            str(geography_record.geography_code)
            if geography_record and geography_record.geography_code
            else None
        ),
    }

    # Don't pass on any rubbish
    normalized_requested_filters: dict[PermissionFilterResource, str] = {
        key: str(value)
        for key, value in requested_filters.items()
        if _permission_value_is_valid(value)
    }

    matching_permissions = filter_permissions(
        jwt_permissions=jwt_permissions,
        requested_filters=normalized_requested_filters,
    )

    return bool(matching_permissions)


def filter_permissions(
    *,
    jwt_permissions: dict | None,
    requested_filters: dict[PermissionFilterResource, str],
) -> list[dict[str, str]]:
    """
    Filter permissions that match the requested IDs.
    Returns a list of matching permissions containing IDs (without wildcards "-1").

    @param {dict | None} jwt_permissions, eg:
            {
                "permission_set_hierarchy": [
                    {
                        "theme": {"id": "100", "name": "immunisation"},
                        "sub_theme": {"id": "133", "name": "childhood-vaccines"},
                        "topic": {"id": "215", "name": "MMR1"},
                    }
                ]
            }

    @param {dict} requested_filters, eg:
            {"theme": "100", "sub_theme": "133", "topic": "114"}

    @return {list}, eg:
            [{"theme": "100", "sub_theme": "133"}]
    """

    if not isinstance(
        permission_set_hierarchy := (jwt_permissions or {}).get(
            "permission_set_hierarchy"
        ),
        list,
    ):
        return []

    if not requested_filters:
        return []

    matching_permissions: list[dict[str, str]] = []

    for permission in permission_set_hierarchy:
        if not isinstance(permission, dict) or not permission:
            continue

        concrete_filters: dict[str, str] = {}

        # Permission row must satisfy all requested dimensions, not just some
        for filter_key, requested_value in requested_filters.items():
            permission_value = _extract_permission_id(
                permission=permission,
                filter_key=filter_key,
            )

            if permission_value == requested_value:
                # Exact permission match also grants access on this dimension.
                concrete_filters[filter_key] = requested_value
                continue
            if permission_value == "-1":
                # Wildcard grants access on this dimension.
                concrete_filters[filter_key] = requested_value
                continue

            # This permission row did not satisfy all requested filters
            break
        else:
            # Only runs if loop didn't break -> full match.
            matching_permissions.append(concrete_filters)

    return matching_permissions


def _extract_permission_id(
    *, permission: dict[str, object], filter_key: PermissionFilterResource
) -> str | None:
    """
    Extract a permission id for one filter key from a permission entry.

    @param {dict} permission, eg:
            {
                "theme": {"id": "100", "name": "immunisation"},
                "sub_theme": {"id": "133", "name": "childhood-vaccines"},
                "topic": {"id": "-1", "name": "* (All)"},
            }

    @param {str} filter_key, eg:
        "sub_theme"

    @return {str | None}, eg:
        "133"
    """

    # Do we offer permissions on this resource?
    if filter_key not in permission:
        return None

    # Is permission resource present?
    permission_resource = permission.get(filter_key)
    if not permission_resource:
        return None

    # Permission resource malformed?
    if not isinstance(permission_resource, dict):
        return None

    # Does it have a meaningful permission value?
    permission_id = permission_resource.get("id")
    if not _permission_value_is_valid(permission_id):
        return None

    # Return ID, if all is fine until here
    return str(permission_id)


def _permission_value_is_valid(value: object) -> bool:
    """
    Is value a valid permission ID?

    A valid permission value is an integer-like value except 0.
    Integers that exist as string types are fine, eg "5" instead of 5.
    The wildcard "-1" remains also valid.
    """
    if value is None:
        return False

    if isinstance(value, bool):
        return False

    value_as_text = str(value).strip()

    if not value_as_text:
        return False

    try:
        numeric_value = int(value_as_text)
    except (TypeError, ValueError):
        return False

    return numeric_value != 0


class InvalidPermissionHierarchyError(ValueError):
    """
    Raised when a JWT permission hierarchy contains invalid values
    """
