from collections import defaultdict

from rest_framework import serializers

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
            self.core_time_series_manager.get_available_geographies(topic=topic)
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
