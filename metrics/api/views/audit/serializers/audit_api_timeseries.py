from datetime import datetime

from rest_framework import serializers

from metrics.api.views.audit.shared import EXPECTED_TIMESTAMP_FORMAT
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
    def get_refresh_date(cls, obj: APITimeSeries) -> str:
        return datetime.strftime(obj.refresh_date, EXPECTED_TIMESTAMP_FORMAT)

    @classmethod
    def get_embargo(cls, obj: APITimeSeries) -> str:
        try:
            return datetime.strftime(obj.embargo, EXPECTED_TIMESTAMP_FORMAT)
        except TypeError:
            return ""
