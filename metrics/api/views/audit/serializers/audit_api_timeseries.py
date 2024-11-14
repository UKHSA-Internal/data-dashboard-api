from datetime import datetime

from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries


class AuditAPITimeSeriesSerializer(serializers.ModelSerializer):
    """This serializer returns a set of serialized fields from the `APITimeseries`.

    The `SerializerMethodField()` and `get_<field_name>()` methods are used to override
    the data fields to format `date` fields to make them more readable.
    """

    refresh_date = serializers.SerializerMethodField()
    embargo = serializers.SerializerMethodField()

    class Meta:
        model = APITimeSeries
        fields = "__all__"

    @classmethod
    def get_refresh_date(cls, obj) -> str:
        return datetime.strftime(obj.refresh_date, "%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_embargo(cls, obj) -> str:
        return datetime.strftime(obj.embargo, "%Y-%m-%d %H:%M:%S")
