from django.db.models import QuerySet
from rest_framework import serializers

from metrics.data.models.constants import PERMISSION_SET_WILDCARD_ID_VALUE
from metrics.data.models.core_models.supporting import Metric, SubTheme, Topic


def _validate_input_id(value, field_name):
    """Validate theme_id is either wildcard or a valid integer"""
    if value == PERMISSION_SET_WILDCARD_ID_VALUE:
        return value

    try:
        int(value)
    except ValueError as err:
        msg = f"{field_name} must be a number or '-1'"
        raise serializers.ValidationError(msg) from err
    else:
        return value


class SubThemeRequestSerializer(serializers.Serializer):
    """Fetches and formats sub-theme choices based on theme_id"""

    theme_id = serializers.CharField(required=True)

    @property
    def sub_theme_manager(self):
        """
        Fetch the topic manager from the context if available.
        If not get the Manager which has been declared on the `Topic` model.
        """
        return self.context.get("sub_theme_manager", SubTheme.objects)

    @staticmethod
    def validate_theme_id(value):
        """Validate theme_id is either wildcard or a valid integer"""
        return _validate_input_id(value, "theme_id")

    def data(self) -> dict:
        """
        Fetch sub-themes from DB and format as response.

        Returns:
            Dict with 'choices' key containing list of [id, name] pairs
        """
        theme_id = self.validated_data["theme_id"]

        if theme_id == PERMISSION_SET_WILDCARD_ID_VALUE:
            return {
                "choices": [[PERMISSION_SET_WILDCARD_ID_VALUE, "* (All sub-themes)"]]
            }

        parent_theme_id = int(theme_id)
        sub_theme_tuples = _queryset_to_id_name_tuples(
            self.sub_theme_manager.get_filtered_unique_names_related_to_theme(
                parent_theme_id
            )
        )
        choices = [[str(item_id), name] for item_id, name in sub_theme_tuples]

        return {"choices": choices}


class TopicRequestSerializer(serializers.Serializer):
    """Fetches and formats topic related to sub-themes based on provided parent sub_theme_id"""

    sub_theme_id = serializers.CharField(required=True)

    @property
    def topic_manager(self):
        """
        Fetch the topic manager from the context if available.
        If not get the Manager which has been declared on the `Topic` model.
        """
        return self.context.get("topic_manager", Topic.objects)

    @staticmethod
    def validate_sub_theme_id(value):
        """Validate sub_theme_id is either wildcard or a valid integer"""
        return _validate_input_id(value, "sub_theme_id")

    def data(self) -> dict:
        """
        Fetch topics from DB and format as response.

        Returns:
            Dict with 'choices' key containing list of [id, name] pairs
        """
        sub_theme_id = self.validated_data["sub_theme_id"]

        if sub_theme_id == PERMISSION_SET_WILDCARD_ID_VALUE:
            return {"choices": [[PERMISSION_SET_WILDCARD_ID_VALUE, "* (All topics)"]]}

        parent_sub_theme_id = int(sub_theme_id)
        topic_tuples = _queryset_to_id_name_tuples(
            self.topic_manager.get_filtered_unique_names_related_to_sub_theme(
                parent_sub_theme_id
            )
        )

        choices = [[str(item_id), name] for item_id, name in topic_tuples]

        return {"choices": choices}


class MetricRequestSerializer(serializers.Serializer):
    """Fetches and formats metrics related to topics based on provided parent topic_id"""

    topic_id = serializers.CharField(required=True)

    @property
    def metric_manager(self):
        """
        Fetch the metric manager from the context if available.
        If not get the Manager which has been declared on the `Metric` model.
        """
        return self.context.get("metric_manager", Metric.objects)

    @staticmethod
    def validate_topic_id(value):
        """Validate topic_id is either wildcard or a valid integer"""
        return _validate_input_id(value, "topic_id")

    def data(self) -> dict:
        """
        Fetch topics from DB and format as response.

        Returns:
            Dict with 'choices' key containing list of [id, name] pairs
        """
        topic_id = self.validated_data["topic_id"]

        if topic_id == PERMISSION_SET_WILDCARD_ID_VALUE:
            return {"choices": [[PERMISSION_SET_WILDCARD_ID_VALUE, "* (All metrics)"]]}

        parent_topic_id = int(topic_id)
        metric_tuples = _queryset_to_id_name_tuples(
            self.metric_manager.get_filtered_unique_names_related_to_parent_topic_id(
                parent_topic_id
            )
        )

        choices = [[str(item_id), name] for item_id, name in metric_tuples]

        return {"choices": choices}


class PermissionSetResponseSerializer(serializers.Serializer):
    """Formats the response for choice endpoints"""

    choices = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(), min_length=2, max_length=2
        ),
        help_text="List of [id, name] pairs for dropdown options",
    )


def _queryset_to_id_name_tuples(queryset: QuerySet) -> list[tuple[int, str]]:
    """
    Convert a QuerySet with 'id' and 'name' fields to a list of tuples.

    Args:
        queryset: QuerySet containing dicts with 'id' and 'name' keys

    Returns:
        List of (id, name) tuples

    Examples:
        >>> qs = Model.objects.values('id', 'name')
        >>> queryset_to_id_name_tuples(qs)
        [(1, "item1"), (2, "item2")]
    """
    return [(item["id"], item["name"]) for item in queryset]
