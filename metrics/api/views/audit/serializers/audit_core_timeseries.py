from datetime import datetime

from rest_framework import serializers

from metrics.data.models.core_models import CoreTimeSeries


class AuditCoreTimeseriesSerializer(serializers.ModelSerializer):
    """This serializer returns a set of serialized fields from the `CoreTimeseries` and realated models.

    The `SerializerMethodField()` and `get_<field_name>()` methods enable us to map fields from
    supporting models for the serialized payload.

    Eg: `obj.metric.topic.sub_theme.theme.name` becomes theme
    """

    topic = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()
    sub_theme = serializers.SerializerMethodField()
    metric = serializers.SerializerMethodField()
    geography = serializers.SerializerMethodField()
    geography_type = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    stratum = serializers.SerializerMethodField()
    refresh_date = serializers.SerializerMethodField()
    embargo = serializers.SerializerMethodField()

    class Meta:
        model = CoreTimeSeries
        fields = "__all__"

    @classmethod
    def get_topic(cls, obj) -> str:
        return obj.metric.topic.name

    @classmethod
    def get_theme(cls, obj) -> str:
        return obj.metric.metric_group.topic.sub_theme.theme.name

    @classmethod
    def get_sub_theme(cls, obj) -> str:
        return obj.metric.metric_group.topic.sub_theme.name

    @classmethod
    def get_metric(cls, obj) -> str:
        return obj.metric.name

    @classmethod
    def get_geography(cls, obj) -> str:
        return obj.geography.name

    @classmethod
    def get_geography_type(cls, obj) -> str:
        return obj.geography.geography_type.name

    @classmethod
    def get_age(cls, obj) -> str:
        return obj.age.name

    @classmethod
    def get_stratum(cls, obj) -> str:
        return obj.stratum.name

    @classmethod
    def get_refresh_date(cls, obj) -> str:
        return datetime.strftime(obj.refresh_date, "%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_embargo(cls, obj) -> str:
        return datetime.strftime(obj.embargo, "%Y-%m-%d %H:%M:%S")
