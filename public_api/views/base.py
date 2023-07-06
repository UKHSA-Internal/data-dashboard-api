from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.serializers.api_time_series_request_serializer import (
    APITimeSeriesDTO,
    APITimeSeriesRequestSerializer,
)

PUBLIC_API_TAG = "public-api"


class BaseNestedAPITimeSeriesView(GenericAPIView):
    queryset = MetricsPublicAPIInterface.get_api_timeseries_model().objects.all()

    @property
    def lookup_field(self):
        raise NotImplementedError()

    @property
    def serializer_class(self):
        raise NotImplementedError()

    def _build_request_serializer(
        self, request: Request
    ) -> APITimeSeriesRequestSerializer:
        serializer_context = {"request": request, "lookup_field": self.lookup_field}
        return APITimeSeriesRequestSerializer(context=serializer_context)

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer: APITimeSeriesRequestSerializer = self._build_request_serializer(
            request=request
        )
        timeseries_dto_slice: list[
            APITimeSeriesDTO
        ] = serializer.build_timeseries_dto_slice()

        serializer = self.get_serializer(timeseries_dto_slice, many=True)
        return Response(serializer.data)
