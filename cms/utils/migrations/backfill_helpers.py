from wagtail.fields import StreamValue


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


def backfill_pages_with_theme_and_subtheme(apps, model_section, model_name):
    topic_map = _build_topic_map(apps)

    LandingPage = apps.get_model(model_section, model_name)

    for page in LandingPage.objects.all().iterator():
        if not page.body:
            continue

        raw_data = page.body.get_prep_value()

        if not _fill_node(raw_data, topic_map):
            continue

        page.body = StreamValue(page.body.stream_block, raw_data, is_lazy=True)
        page.save(update_fields=["body"])
