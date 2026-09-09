"""
This file contains a set of utility functions for handling the backfill of data via Django migrations.

backfill_pages_with_theme_and_subtheme was introduced when changes were added to the codebase
that made theme and subtheme mandatory across all pages. Introducing this would be a breaking
change that would require extensive changes throughout the CMS following deployment if not
automated. These functions apply the required changes throughout the database to prevent
any potential downtime, or error pages encountered by users due to a schema mismatch.
"""

import json
from wagtail.fields import StreamValue


def backfill_pages_with_theme_and_subtheme(apps, model_section, model_name):
    topic_map = _build_topic_map(apps)

    app_model = apps.get_model(model_section, model_name)

    for page in app_model.objects.all().iterator():
        if not page.body:
            continue

        raw_data = page.body.get_prep_value()

        if not _fill_node(raw_data, topic_map):
            continue

        page.body = StreamValue(page.body.stream_block, raw_data, is_lazy=True)
        page.save(update_fields=["body"])

    _backfill_revisions_for_content_type(apps, model_section, model_name, topic_map)


def _build_topic_map(apps):
    Topic = apps.get_model("data", "Topic")

    topic_map = {}
    for topic in Topic.objects.select_related("sub_theme__theme"):
        sub_theme = topic.sub_theme
        if sub_theme and sub_theme.theme:
            topic_map[topic.name] = (sub_theme.theme.name, sub_theme.name)
    return topic_map


def _fill_node(node, topic_map) -> bool:
    """Recursively fill theme/sub_theme on any plot, operating on raw dicts/lists."""
    changed = False

    if isinstance(node, dict):
        topic = node.get("topic")

        if isinstance(topic, str) and topic in topic_map:
            theme_name, sub_theme_name = topic_map[topic]

            if not node.get("theme"):
                node["theme"] = theme_name
                changed = True

            if not node.get("sub_theme"):
                node["sub_theme"] = sub_theme_name
                changed = True

        for value in node.values():
            changed |= _fill_node(value, topic_map)
    elif isinstance(node, list):
        for item in node:
            changed |= _fill_node(item, topic_map)

    return changed


def _backfill_revisions_for_content_type(apps, model_section, model_name, topic_map):
    revision_model = apps.get_model("wagtailcore", "Revision")
    content_type_model = apps.get_model("contenttypes", "ContentType")

    try:
        content_type = content_type_model.objects.get(
            app_label=model_section, model=model_name.lower()
        )
    except content_type_model.DoesNotExist:
        return

    revisions = revision_model.objects.filter(content_type=content_type).iterator()

    updated = []
    for revision in revisions:
        content = revision.content
        raw_body = content.get("body")

        if not raw_body:
            continue

        body_data = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        if not _fill_node(body_data, topic_map):
            continue

        content["body"] = (
            json.dumps(body_data) if isinstance(raw_body, str) else body_data
        )
        revision.content = content
        updated.append(revision)

    if updated:
        revision_model.objects.bulk_update(updated, ["content"], batch_size=500)
