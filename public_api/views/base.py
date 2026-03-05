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
        raise NotImplementedError

    @property
    def serializer_class(self):
        raise NotImplementedError

    def _build_request_serializer(
        self, *, request: Request
    ) -> APITimeSeriesRequestSerializer:
        serializer_context = {"request": request, "lookup_field": self.lookup_field}
        return APITimeSeriesRequestSerializer(context=serializer_context)

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request: Request, *args, **kwargs) -> Response:
        
        try:
            is_public = request.query_params["is-public"]
        except KeyError:
            is_public = "True"
            
        # TODO: as part of CDD-3173, the JWT will need validating, and it should be confirmed that, if is_public is false, there is a valid JWT before returning non public data
        
        serializer: APITimeSeriesRequestSerializer = self._build_request_serializer(
            request=request
        )
        timeseries_dto_slice: list[APITimeSeriesDTO] = (
            serializer.build_timeseries_dto_slice()
        )

        serializer = self.get_serializer(timeseries_dto_slice, many=True)
        response = Response(data=serializer.data)

        # if valid_jwt and not is_public :
        if is_public == "False" :
             response.headers["Cache-Control"] = "private, no-cache"
            
        return response
