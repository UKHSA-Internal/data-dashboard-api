from collections import defaultdict

from rest_framework import serializers

from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreTimeSeries, Geography, GeographyType, Topic


class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = ["id", "name"]


class GeographyTypesDetailSerializer(serializers.ModelSerializer):
    geographies = GeographySerializer(many=True, read_only=True)

    class Meta:
        model = GeographyType
        fields = ["geographies"]


class GeographyTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographyType
        fields = ["id", "name"]


GEOGRAPHY_TYPE_RESULT = dict[str, list[dict[str, str]]]


class GeographiesSerializer(serializers.Serializer):
    topic = serializers.CharField()

    def validate_topic(self, value):
        if not self.topic_manager.does_topic_exist(topic=value):
            raise serializers.ValidationError({"name": "Please enter a valid topic name."})

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
                    "geographies": [{"name": "Birmingham"}, {"name": "Leeds"}],
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
        merged_geographies[geography_type].append({"name": geography})

    return [
        {"geography_type": geography_type, "geographies": geographies}
        for geography_type, geographies in merged_geographies.items()
    ]
