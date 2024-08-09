from rest_framework.serializers import Serializer

from public_api.serializers.api_time_series_request_serializer import (
    APITimeSeriesRequestSerializer,
)
from public_api.v2.serializers.api_time_series_request_serializer import (
    APITimeSeriesRequestSerializerV2,
)


def return_request_serializer(*, serializer_context: dict[str]) -> Serializer:
    """Returns a Serializer based on the request version number."""
    if serializer_context["request"].version == "v1":
        return APITimeSeriesRequestSerializer(context=serializer_context)

    return APITimeSeriesRequestSerializerV2(context=serializer_context)
