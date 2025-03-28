from rest_framework.serializers import Serializer


def remove_none_from_serializer_data(*, serializer: Serializer) -> list[dict]:
    """Removes `None` values from a serializer's data list.

    Notes:
        When `serializer.data` may include `None` entries,
        which can occur if some objects in the serializer's queryset
        are excluded or filtered out during serialization.

    Returns:
        cleaned_data: A list of dictionaries with all `None` values removed.
    """
    return [item for item in serializer.data if item is not None]
