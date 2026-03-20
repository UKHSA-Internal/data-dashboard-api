from rest_framework import serializers

from metrics.data.models.core_models.supporting import SubTheme
from django.db.models import QuerySet


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

    def validate_theme_id(self, value):
        """Validate theme_id is either wildcard or a valid integer"""
        if value == "-1":
            return value

        try:
            int(value)
            return value
        except ValueError:
            raise serializers.ValidationError(
                "theme_id must be a number or '-1'")

    def data(self) -> dict:
        """
        Fetch sub-themes from DB and format as response.

        Returns:
            Dict with 'choices' key containing list of [id, name] pairs
        """
        theme_id = self.validated_data['theme_id']

        # Handle wildcard
        if theme_id == "-1":
            return {'choices': [["-1", "* (All sub-themes)"]]}

        # Fetch from interface
        parent_theme_id = int(theme_id)
        sub_theme_tuples = _queryset_to_id_name_tuples(self.sub_theme_manager.get_filtered_unique_names_related_to_theme(
            parent_theme_id))

        # Format response
        print('sub_themes: ', sub_theme_tuples)
        choices = [[str(id), name] for id, name in sub_theme_tuples]

        return {'choices': choices}


class PermissionSetResponseSerializer(serializers.Serializer):
    """Formats the response for choice endpoints"""
    choices = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(),
            min_length=2,
            max_length=2
        ),
        help_text="List of [id, name] pairs for dropdown options"
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
    return [(item['id'], item['name']) for item in queryset]
