"""
Permission grouping utilities for organizing deduplicated permissions.

This module provides functionality to group permissions by various dimensions
(geography_type, theme, etc.) for different UI/API use cases.
"""

from collections import defaultdict
from typing import Any

from metrics.utils.permission_hierarchy import NormalizedPermission


def group_by_geography_type(
    permissions: list[NormalizedPermission],
) -> dict[str, Any]:
    """
    Group permissions by geography type, then by specific geography.

    Structure:
    {
        "All Geography Types": {
            "*": {
                "geography_name": "All Geographies",
                "geography_code": "*",
                "permissions": [...]
            }
        },
        "Nation": {
            "E92000001": {
                "geography_name": "England",
                "geography_code": "E92000001",
                "permissions": [...]
            }
        },
        "Region": {
            "E12000008": {
                "geography_name": "South East",
                "geography_code": "E12000008",
                "permissions": [...]
            }
        }
    }

    Args:
        permissions: List of deduplicated NormalizedPermission objects

    Returns:
        Nested dict grouped by geography type, then geography code
    """
    grouped = defaultdict(lambda: defaultdict(lambda: {
        "geography_name": None,
        "geography_code": None,
        "permissions": []
    }))

    for perm in permissions:
        # Determine geography type display name
        if perm.geography_type_id == "-1":
            geo_type_display = "All Geography Types"
        else:
            geo_type_display = perm.geography_type_name

        # Determine geography code/display
        if perm.geography_id == "-1":
            geo_code = "*"
            geo_name = f"All {geo_type_display}s" if perm.geography_type_id != "-1" else "All Geographies"
        else:
            geo_code = perm.geography_id
            geo_name = perm.geography_name

        # Initialize geography entry if needed
        if not grouped[geo_type_display][geo_code]["geography_name"]:
            grouped[geo_type_display][geo_code]["geography_name"] = geo_name
            grouped[geo_type_display][geo_code]["geography_code"] = geo_code

        # Add permission to this geography
        grouped[geo_type_display][geo_code]["permissions"].append({
            "theme": {
                "id": perm.theme_id or None,
                "name": perm.theme_name or None,
            },
            "sub_theme": {
                "id": perm.sub_theme_id or None,
                "name": perm.sub_theme_name or None,
            },
            "topic": {
                "id": perm.topic_id or None,
                "name": perm.topic_name or None,
            },
            "metric": {
                "id": perm.metric_id or None,
                "name": perm.metric_name or None,
            },
        })

    # Convert defaultdict to regular dict for JSON serialization
    return {k: dict(v) for k, v in grouped.items()}


def group_by_theme(
    permissions: list[NormalizedPermission],
) -> dict[str, Any]:
    """
    Group permissions by theme hierarchy.

    Structure:
    {
        "infectious_disease": {
            "theme_id": "2",
            "sub_themes": {
                "respiratory": {
                    "sub_theme_id": "2",
                    "topics": {
                        "COVID-19": {
                            "topic_id": "3",
                            "geographies": [...]
                        }
                    }
                }
            }
        }
    }

    Args:
        permissions: List of deduplicated NormalizedPermission objects

    Returns:
        Nested dict grouped by theme → sub-theme → topic
    """
    grouped = defaultdict(lambda: {
        "theme_id": None,
        "sub_themes": defaultdict(lambda: {
            "sub_theme_id": None,
            "topics": defaultdict(lambda: {
                "topic_id": None,
                "geographies": []
            })
        })
    })

    for perm in permissions:
        theme_key = perm.theme_name or perm.theme_id
        sub_theme_key = perm.sub_theme_name or perm.sub_theme_id
        topic_key = perm.topic_name or perm.topic_id

        # Set IDs if not already set
        if not grouped[theme_key]["theme_id"]:
            grouped[theme_key]["theme_id"] = perm.theme_id

        if not grouped[theme_key]["sub_themes"][sub_theme_key]["sub_theme_id"]:
            grouped[theme_key]["sub_themes"][sub_theme_key]["sub_theme_id"] = perm.sub_theme_id

        if not grouped[theme_key]["sub_themes"][sub_theme_key]["topics"][topic_key]["topic_id"]:
            grouped[theme_key]["sub_themes"][sub_theme_key]["topics"][topic_key]["topic_id"] = perm.topic_id

        # Add geography to this topic
        grouped[theme_key]["sub_themes"][sub_theme_key]["topics"][topic_key]["geographies"].append({
            "geography_type": {
                "id": perm.geography_type_id or None,
                "name": perm.geography_type_name or None,
            },
            "geography": {
                "id": perm.geography_id or None,
                "name": perm.geography_name or None,
            },
            "metric": {
                "id": perm.metric_id or None,
                "name": perm.metric_name or None,
            },
        })

    # Convert nested defaultdicts to regular dicts
    result = {}
    for theme_key, theme_data in grouped.items():
        result[theme_key] = {
            "theme_id": theme_data["theme_id"],
            "sub_themes": {}
        }
        for sub_theme_key, sub_theme_data in theme_data["sub_themes"].items():
            result[theme_key]["sub_themes"][sub_theme_key] = {
                "sub_theme_id": sub_theme_data["sub_theme_id"],
                "topics": {}
            }
            for topic_key, topic_data in sub_theme_data["topics"].items():
                result[theme_key]["sub_themes"][sub_theme_key]["topics"][topic_key] = dict(
                    topic_data)

    return result
