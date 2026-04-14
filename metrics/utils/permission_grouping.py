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
        "1": {  # geography_type_id
            "geography_type_name": "Region",
            "geographies": {
                "E12000008": {  # geography_id (code)
                    "geography_name": "South East",
                    "permissions": [...]
                }
            }
        },
        "-1": {  # wildcard geography_type_id
            "geography_type_name": "All Geography Types",
            "geographies": {
                "*": {
                    "geography_name": "All Geographies",
                    "permissions": [...]
                }
            }
        }
    }

    Args:
        permissions: List of deduplicated NormalizedPermission objects

    Returns:
        Nested dict grouped by geography type ID, then geography code
    """
    grouped = defaultdict(lambda: {
        "geography_type_name": None,
        "geographies": defaultdict(lambda: {
            "geography_name": None,
            "permissions": []
        })
    })

    for perm in permissions:
        # Use ID as the key (handles wildcards and specific types)
        geo_type_id = perm.geography_type_id or "*"
        geo_code = perm.geography_id if perm.geography_id != "-1" else "*"

        # Set geography type name if not already set
        if not grouped[geo_type_id]["geography_type_name"]:
            if geo_type_id == "-1" or geo_type_id == "*":
                grouped[geo_type_id]["geography_type_name"] = "All Geography Types"
            else:
                grouped[geo_type_id]["geography_type_name"] = perm.geography_type_name

        # Set geography name if not already set
        if not grouped[geo_type_id]["geographies"][geo_code]["geography_name"]:
            if geo_code == "*":
                if geo_type_id == "-1" or geo_type_id == "*":
                    geo_name = "All Geographies"
                else:
                    geo_name = f"All {perm.geography_type_name}s"
            else:
                geo_name = perm.geography_name
            grouped[geo_type_id]["geographies"][geo_code]["geography_name"] = geo_name

        # Add permission to this geography
        grouped[geo_type_id]["geographies"][geo_code]["permissions"].append({
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
    result = {}
    for geo_type_id, geo_type_data in grouped.items():
        result[geo_type_id] = {
            "geography_type_name": geo_type_data["geography_type_name"],
            "geographies": dict(geo_type_data["geographies"])
        }

    return result


def group_by_theme(
    permissions: list[NormalizedPermission],
) -> dict[str, Any]:
    """
    Group permissions by theme hierarchy using IDs as keys.

    Structure:
    {
        "2": {  # theme_id
            "theme_name": "infectious_disease",
            "sub_themes": {
                "2": {  # sub_theme_id
                    "sub_theme_name": "respiratory",
                    "topics": {
                        "3": {  # topic_id
                            "topic_name": "COVID-19",
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
        Nested dict grouped by theme_id → sub_theme_id → topic_id
    """
    grouped = defaultdict(lambda: {
        "theme_name": None,
        "sub_themes": defaultdict(lambda: {
            "sub_theme_name": None,
            "topics": defaultdict(lambda: {
                "topic_name": None,
                "geographies": []
            })
        })
    })

    for perm in permissions:
        # Use IDs as keys (handles wildcards and specific IDs)
        theme_id = perm.theme_id or "*"
        sub_theme_id = perm.sub_theme_id or "*"
        topic_id = perm.topic_id or "*"

        # Set names if not already set
        if not grouped[theme_id]["theme_name"]:
            grouped[theme_id]["theme_name"] = perm.theme_name

        if not grouped[theme_id]["sub_themes"][sub_theme_id]["sub_theme_name"]:
            grouped[theme_id]["sub_themes"][sub_theme_id]["sub_theme_name"] = perm.sub_theme_name

        if not grouped[theme_id]["sub_themes"][sub_theme_id]["topics"][topic_id]["topic_name"]:
            grouped[theme_id]["sub_themes"][sub_theme_id]["topics"][topic_id]["topic_name"] = perm.topic_name

        # Add geography to this topic
        grouped[theme_id]["sub_themes"][sub_theme_id]["topics"][topic_id]["geographies"].append({
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

    # Convert nested default dicts to regular dicts
    result = {}
    for theme_id, theme_data in grouped.items():
        result[theme_id] = {
            "theme_name": theme_data["theme_name"],
            "sub_themes": {}
        }
        for sub_theme_id, sub_theme_data in theme_data["sub_themes"].items():
            result[theme_id]["sub_themes"][sub_theme_id] = {
                "sub_theme_name": sub_theme_data["sub_theme_name"],
                "topics": {}
            }
            for topic_id, topic_data in sub_theme_data["topics"].items():
                result[theme_id]["sub_themes"][sub_theme_id]["topics"][topic_id] = dict(
                    topic_data
                )

    return result