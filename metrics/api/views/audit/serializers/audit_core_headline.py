from datetime import datetime

from rest_framework import serializers

from metrics.api.views.audit.shared import EXPECTED_TIMESTAMP_FORMAT
from metrics.data.models.core_models import CoreHeadline


class AuditCoreHeadlineSerializer(serializers.ModelSerializer):
    """This serializer returns a set of serialized fields from the `CoreHeadline` and related models.

    The `SerializerMethodField()` and `get_<field_name>()` methods enable us to map fields from
    supporting models for the serialized payload.

    Eg: `obj.metric.topic.sub_theme.theme.name` becomes theme
    """

    theme = serializers.SerializerMethodField()
    sub_theme = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    geography_type = serializers.SerializerMethodField()
    geography = serializers.SerializerMethodField()
    geography_code = serializers.SerializerMethodField()
    metric = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    stratum = serializers.SerializerMethodField()
    period_start = serializers.SerializerMethodField()
    period_end = serializers.SerializerMethodField()
    refresh_date = serializers.SerializerMethodField()
    embargo = serializers.SerializerMethodField()

    class Meta:
        model = CoreHeadline
        fields = "__all__"

    @classmethod
    def get_topic(cls, obj: CoreHeadline) -> str:
        return obj.metric.topic.name

    @classmethod
    def get_theme(cls, obj: CoreHeadline) -> str:
        return obj.metric.topic.sub_theme.theme.name

    @classmethod
    def get_sub_theme(cls, obj: CoreHeadline) -> str:
        return obj.metric.topic.sub_theme.name

    @classmethod
    def get_metric(cls, obj: CoreHeadline) -> str:
        return obj.metric.name

    @classmethod
    def get_geography(cls, obj: CoreHeadline) -> str:
        return obj.geography.name

    @classmethod
    def get_geography_type(cls, obj: CoreHeadline) -> str:
        return obj.geography.geography_type.name

    @classmethod
    def get_geography_code(cls, obj: CoreHeadline) -> str:
        return obj.geography.geography_code

    @classmethod
    def get_age(cls, obj: CoreHeadline) -> str:
        return obj.age.name

    @classmethod
    def get_stratum(cls, obj: CoreHeadline) -> str:
        return obj.stratum.name

    @classmethod
    def get_period_start(cls, obj: CoreHeadline) -> str:
        return datetime.strftime(obj.period_start, EXPECTED_TIMESTAMP_FORMAT)

    @classmethod
    def get_period_end(cls, obj: CoreHeadline) -> str:
        return datetime.strftime(obj.period_end, EXPECTED_TIMESTAMP_FORMAT)

    @classmethod
    def get_refresh_date(cls, obj: CoreHeadline) -> str:
        return datetime.strftime(obj.refresh_date, EXPECTED_TIMESTAMP_FORMAT)

    @classmethod
    def get_embargo(cls, obj: CoreHeadline) -> str:
        try:
            return datetime.strftime(obj.embargo, EXPECTED_TIMESTAMP_FORMAT)
        except TypeError:
            return ""
