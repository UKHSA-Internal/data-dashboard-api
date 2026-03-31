from collections import defaultdict

from django.db.models import QuerySet
from rest_framework import serializers

from auth_content.constants import WILDCARD_ID_VALUE
from metrics.api.serializers import help_texts
from metrics.data.in_memory_models.geography_relationships.handlers import (
    get_upstream_relationships_for_geography,
)
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import (
    CoreTimeSeries,
    Geography,
    Topic,
)

GEOGRAPHY_TYPE_RESULT = dict[str, list[dict[str, str]]]


class GeographiesForTopicSerializer(serializers.Serializer):
    topic = serializers.CharField()

    def validate_topic(self, value):
        if not self.topic_manager.does_topic_exist(topic=value):
            raise serializers.ValidationError(
                {"name": "Please enter a valid topic name."}
            )

        return value

    @property
    def topic_manager(self):
        """
        Fetch the topic manager from the context if available.
        If not get the Manager which has been declared on the `Topic` model.
        """
        return self.context.get("topic_manager", Topic.objects)

    @property
    def core_time_series_manager(self):
        """
        Fetch the core_time_series_manager from the context if available.
        If not get the Manager which has been declared on the `CoreTimeSeries` model.
        """
        return self.context.get("core_time_series_manager", CoreTimeSeries.objects)

    def data(self) -> list[GEOGRAPHY_TYPE_RESULT]:
        """Finds available geography types as list of dicts, where each dict represents a geography_type

        Examples:
          >>>> [
                {"geography_type": "Nation", "geographies": [{"name": "England"}]},
                {
                    "geography_type": "Lower Tier Local Authority",
                    "geographies": [{"name": "Birmingham"}, {"name": "Leeds"}],
                },
            ]

        Returns:
            List of dicts representing each geography_type with
            aggregated geographies

        """
        topic: str = self.validated_data["topic"]
        queryset: CoreTimeSeriesQuerySet = (
            self.core_time_series_manager.get_available_geographies(
                topic=topic)
        )
        return _serialize_queryset(queryset=queryset)


def _serialize_queryset(
    *,
    queryset: CoreTimeSeriesQuerySet,
) -> list[GEOGRAPHY_TYPE_RESULT]:
    """Converts the `queryset` to a list of dicts, where each dict represents a geography_type

    Args:
        queryset: The resulting `CoreTimeSeriesQuerySet`
            which has been sliced for the available geographies
            and their corresponding geography types

    Examples:
        A given `queryset` of:
          >>> <CoreTimeSeriesQuerySet [
                Row(geography__name='England', geography__geography_type__name='Nation')
                Row(geography__name='Birmingham', geography__geography_type__name='Lower Tier Local Authority'),
                Row(geography__name='Leeds', geography__geography_type__name='Lower Tier Local Authority'),
                ]
            >

        Would return:
          >>>> [
                {"geography_type": "Nation", "geographies": [{"name": "England"}]},
                {
                    "geography_type": "Lower Tier Local Authority",
                    "geographies": [{"name": "Birmingham"}, {"name": "Leeds"} {"relationships": [...]],
                },
            ]

    Returns:
        List of dicts representing each geography_type with
        aggregated geographies.

    """
    merged_geographies = defaultdict(list)

    for geography_combination in queryset:
        geography: str = geography_combination.geography__name
        geography_type: str = geography_combination.geography__geography_type__name
        geography_code: str = geography_combination.geography__geography_code

        relationships = get_upstream_relationships_for_geography(
            geography_type=geography_type,
            geography_code=geography_code,
        )

        merged_geographies[geography_type].append(
            {
                "name": geography,
                "geography_code": geography_code,
                "relationships": relationships,
            }
        )

    return [
        {"geography_type": geography_type, "geographies": geographies}
        for geography_type, geographies in merged_geographies.items()
    ]


class GeographiesForGeographyTypeSerializer(serializers.Serializer):
    geography_type = serializers.CharField()

    @property
    def geography_manager(self):
        return self.context.get("geography_manager", Geography.objects)

    def data(self) -> list[GEOGRAPHY_TYPE_RESULT]:
        """Finds available geographies for the given geography_type

        Examples:
          >>>> [
                {
                    "geography_type": "Lower Tier Local Authority",
                    "geographies": [{"name": "Birmingham", "relationships: [...]}, {"name": "Leeds"}],
                },
            ]

        Returns:
            List of dicts representing the given geography_type with
            aggregated geographies

        """
        geography_type: str = self.validated_data["geography_type"]
        geographies = self.geography_manager.get_geographies_by_geography_type(
            geography_type_name=geography_type,
        )

        for geography in geographies:
            relationships = get_upstream_relationships_for_geography(
                geography_type=geography_type,
                geography_code=geography["geography_code"],
            )
            geography["relationships"] = relationships

        return [{"geography_type": geography_type, "geographies": geographies}]


class GeographiesRequestSerializerDeprecated(serializers.Serializer):
    topic = serializers.CharField()


class GeographiesResponseGeographiesSerializer(serializers.Serializer):
    name = serializers.CharField()
    geography_code = serializers.CharField()


class GeographiesResponseGeographiesListSerializer(serializers.ListSerializer):
    child = GeographiesResponseGeographiesSerializer()


class GeographiesResponseListSerializer(serializers.Serializer):
    geography_type = serializers.CharField()
    geographies = GeographiesResponseGeographiesListSerializer()


class GeographiesResponseSerializer(serializers.ListSerializer):
    child = GeographiesResponseListSerializer()


class GeographyChoicesResponseSerializer(serializers.Serializer):
    """Formats the response for choice endpoints"""

    choices = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(), min_length=2, max_length=2
        ),
        help_text=help_texts.GEOGRAPHY_LIST_FORMATTING,
    )


MISSING_FIELD_ERROR_MESSAGE = "Either 'topic' or 'geography_type' must be provided."
SINGLE_FIELD_ONLY_ERROR_MESSAGE = (
    "Only one of 'topic' or 'geography_type' should be provided, not both."
)


class GeographiesRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(required=False)
    geography_type = serializers.CharField(required=False)

    @classmethod
    def validate(cls, attrs: dict[str, str]) -> dict[str, str]:
        topic: str = attrs.get("topic")
        geography_type: str = attrs.get("geography_type")

        if not topic and not geography_type:
            raise serializers.ValidationError(MISSING_FIELD_ERROR_MESSAGE)

        if topic and geography_type:
            raise serializers.ValidationError(SINGLE_FIELD_ONLY_ERROR_MESSAGE)

        return attrs


class GeographyByGeographyTypeRequestSerializer(serializers.Serializer):
    geography_type_id = serializers.CharField(required=True)

    @property
    def geography_manager(self):
        return self.context.get("geography_manager", Geography.objects)

    @staticmethod
    def validate_geography_type_id(value: str) -> str | int:
        """Validate geography_type_id is either wildcard or a valid integer"""
        if value == WILDCARD_ID_VALUE:
            return value

        try:
            return int(value)
        except ValueError as err:
            message = "Geography Type must be a number or '-1'"
            raise serializers.ValidationError(message) from err

    def data(self) -> dict[str, list[tuple[str, str]]]:
        """
        Fetch geographies for specified geography type from DB and format as response.

        Returns:
            Dict with 'choices' key containing list of [id, name] pairs
        """
        geography_type_id = self.validated_data["geography_type_id"]

        # Handle wildcard
        if geography_type_id == WILDCARD_ID_VALUE:
            return {"choices": [[WILDCARD_ID_VALUE, "* (All geographies)"]]}

        parent_geography_type_id = int(geography_type_id)
        geographies = (
            self.geography_manager.get_geography_codes_and_names_by_geography_type_id(
                parent_geography_type_id
            )
        )
        geography_names_and_codes_tuples = _queryset_to_geography_code_name_tuples(
            geographies
        )

        choices = [
            [str(geography_code), name]
            for geography_code, name in geography_names_and_codes_tuples
        ]
        return {"choices": choices}


def _queryset_to_geography_code_name_tuples(
    queryset: QuerySet,
) -> list[tuple[str, str]]:
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
    return [(item["geography_code"], item["name"]) for item in queryset]
