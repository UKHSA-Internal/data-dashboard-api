from rest_framework import serializers

from metrics.data.models.core_models import CoreTimeSeries
from metrics.utils.auth import serializer_permissions


@serializer_permissions(["theme", "age", "stratum"])
class CoreTimeSeriesSerializer(serializers.ModelSerializer):
    """This serializer returns a set of serialized fields from the `CoreTimesSeries` and related models.

    The `DownloadsInterface`, processes download data. This processing includes
    both merging and casting multiple querysets resulting in related fields
    (through foreign key relations) to be included using double underscore syntax.

    Eg: `metric -> topic -> sub_theme -> theme` becomes `obj.metric__topic__sub_theme__theme__name`

    The `SerializerMethodField()` and `get_<field_name>()` methods enables us to map these to the correct
    field names for the serialized payload.

    Eg: `obj.metric__topic__sub_theme__theme__name` becomes `theme`
    """

    theme = serializers.SerializerMethodField()
    sub_theme = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    geography_type = serializers.SerializerMethodField()
    geography = serializers.SerializerMethodField()
    metric = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    stratum = serializers.SerializerMethodField()

    class Meta:
        """
        The final four fields (sex, year, date, metric_value) belong to the `CoreTimeSeries` model
        and can be pulled directly from there without the use of `SerializerMethodField()`
        """

        model = CoreTimeSeries
        fields = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "age",
            "stratum",
            "sex",
            "year",
            "date",
            "metric_value",
            "in_reporting_delay_period",
        ]

    @classmethod
    def get_theme(cls, obj) -> str:
        return obj.metric__topic__sub_theme__theme__name

    @classmethod
    def get_sub_theme(cls, obj) -> str:
        return obj.metric__topic__sub_theme__name

    @classmethod
    def get_topic(cls, obj) -> str:
        return obj.metric__topic__name

    @classmethod
    def get_metric(cls, obj) -> str:
        return obj.metric__name

    @classmethod
    def get_geography(cls, obj) -> str:
        return obj.geography__name

    @classmethod
    def get_geography_type(cls, obj) -> str:
        return obj.geography__geography_type__name

    @classmethod
    def get_stratum(cls, obj) -> str:
        return obj.stratum__name

    @classmethod
    def get_age(cls, obj) -> str:
        return obj.age__name
