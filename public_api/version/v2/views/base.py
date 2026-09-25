from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from public_api.auth import is_authenticated_request
from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.version.v2.serializers.api_time_series_request_serializer import (
    APITimeSeriesDTO,
    APITimeSeriesRequestSerializerv2,
)

PUBLIC_API_TAG = "public-api-v2"
PRIVATE_CACHE_CONTROL = "private, no-cache"


def add_private_cache_control_header(
    *, request: Request, response: Response
) -> Response:
    """Prevent shared caching of responses made for authenticated consumers."""
    if is_authenticated_request(request):
        response["Cache-Control"] = PRIVATE_CACHE_CONTROL

    return response


class BaseNestedAPITimeSeriesViewV2(GenericAPIView):
    queryset = MetricsPublicAPIInterface.get_api_timeseries_model().objects.all()

    @property
    def lookup_field(self):
        raise NotImplementedError

    @property
    def serializer_class(self):
        raise NotImplementedError

    def _build_request_serializer(
        self, *, request: Request
    ) -> APITimeSeriesRequestSerializerv2:
        serializer_context = {"request": request, "lookup_field": self.lookup_field}
        return APITimeSeriesRequestSerializerv2(context=serializer_context)

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer: APITimeSeriesRequestSerializerv2 = self._build_request_serializer(
            request=request
        )
        timeseries_dto_slice: list[APITimeSeriesDTO] = (
            serializer.build_timeseries_dto_slice()
        )

        serializer = self.get_serializer(timeseries_dto_slice, many=True)
        response = Response(data=serializer.data)

        return add_private_cache_control_header(request=request, response=response)
